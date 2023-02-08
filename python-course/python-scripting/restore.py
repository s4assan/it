#!/usr/bin/env python3

"""Restore script is used to restore data for various backups for any backup
(influxdb, cassandra), any strategy (AWS or Azure).


Usage: restore [-h] [--debug] [--verbose] [--show-last]
               [--download] [--restore] [--restore-keyspaces]
               [--refresh] [--verify] zinfluxdb|cassandra

optional arguments:
  -h, --help           Show this help message and exit
  --debug              Set log level to debug
  --verbose            Set log level to verbose
  --show-last          Show the last available set of backup tarballs
  --download           Download last set of backup tarballs
  --restore            Restore from tarballs in the download directory
  --restore-keyspaces  Restore keyspaces (cassandra only)
  --refresh            Refresh keyspaces (cassandra only)
  --verify             Verify restored data (cassandra only)

Supported database types
------------------------

The last argument to restore script is the type of data being restored.
Currently, we support influxdb (zinfluxdb) and cassandra. The argument passed to
the script is the prefix of the directory used to store the encrypted tarballs
in the storage backend. For example, influxdb data is stored in zinfluxdb-data
and cassandra data is stored in cassandra-data. Going forward, there could be
postgres-data, vault-data, elasticsearch-data in the storage backend, and the
script shall take postgres, vault and elasticsearch as arguments, then.


Last set of backups
-------------------

The last backup set is collection of backup tarballs that would be required to
be downloaded for full restoration. For example, we store incremental backups
for influxdb throughout the week, and take a full backup of influxdb on Sundays.
The last set of backups, on a Sunday (after the full backup was taken), would be
the full backup tarball. On Monday, the last set of backups would be the
incremental backup taken on Monday plus the full backup taken on Sunday.

For cassandra, the last set of backups would be the set of tarballs in the last
backup directory created by the backup script. For example, if the last backup
was taken on May 1st, 2020 at 18:45:34 and the tarballs for each keyspace were
uploaded to cassandra-data/2020-05-01_18-45-34/, then all the tarballs in that
directory comprise the last set of backups.

Download directory
------------------

The encrypted tarballs are downloaded to backup directory in the data directory
of the database. For example, cassandra backup tarballs are downloaded to
cassandra-data directory in /var/lib/cassandra. The influxdb backup tarballs are
downloaded to zinfluxdb-data in /var/lib/influxdb.

"""

from abc import ABC
import os
import sys
import errno
import re
import argparse
import logging
import pathlib
import shutil
import subprocess
from datetime import datetime

import gnupg
import urllib3
import boto3
from azure.storage.blob import BlobServiceClient

from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError
from cassandra.cluster import Cluster # pylint: disable=no-name-in-module
from cassandra.auth import PlainTextAuthProvider
from cassandra.policies import DCAwareRoundRobinPolicy
from cassandra import OperationTimedOut, ReadFailure

from botocore.exceptions import ClientError

ZINFLUXDB = 'zinfluxdb'
CASSANDRA = 'cassandra'
SUPPORTED_DBS = [CASSANDRA, ZINFLUXDB]

AWS_VARS = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'S3_BACKUP_BUCKET']
AZURE_VARS = ['AZURE_BLOB_BACKUP_CONTAINER', 'AZURE_STORAGE_CONNECTION_STRING']

# If the rows restored are more than this much percentage off, we flag an error
# Some tables, like gangesdb_app_inst_flow_dns_cf have high rate of volatility,
# while tables like purusdb.dev_cf have low rate of volatility
HIGH_ERROR_THRESHOLD = 0.40     # 40%
LOW_ERROR_THRESHOLD = 0.05      # 5%


def execute_cmd(cmd):
    """Helper function to execute a command; returns True if successful, False
       otherwise."""
    try:
        proc = subprocess.run(cmd, check=True)
        logging.debug(proc)
    except subprocess.CalledProcessError as error:
        logging.error('Failed to run %s: %s', ' '.join(cmd), error)
        return False
    return True


def row_count_ok(table_name, expected, actual):
    """ Flag if difference in expected and actual rows restored is too much """
    high_error_tbls = ['gangesdb.app_inst_flow_dns_cf']
    if table_name in high_error_tbls:
        threshold = HIGH_ERROR_THRESHOLD
    else:
        threshold = LOW_ERROR_THRESHOLD
    if actual > expected * (1.0 + threshold) or \
       actual < expected * (1.0 - threshold):
        return False
    return True


# pylint: disable=too-few-public-methods
class DataSource(ABC):
    """ Generic Data source """
    def __init__(self, **kwargs):
        self.datatype = kwargs.get('datatype', None)

    def restore(self):
        """ Restore backup from tarballs in data_dir """


class InfluxData(DataSource):
    """ Influxdb Data Source """
    # Influxdb constants
    FULL_BACKUP_SUFFIX = '-full.tar.gz.gpg'
    DATA_DIR = '/var/lib/influxdb'
    BACKUP_DIR = os.path.join(DATA_DIR, 'zinfluxdb-data')

    HOST = '127.0.0.1'
    PORT = 8086

    def __init__(self, *args, **kwargs):
        self.datatype = ZINFLUXDB
        super().__init__(*args, **kwargs)

    def get_last_backup_keys(self, objs):
        """ Return the set of last backups that comprise a full influxdb backup """
        # Assumption: the objects in the backup bucket are chronologically
        # ordered. We iterate over the last 20 objects in reverse order to find the last
        # full backup, while adding them to the list of blobs that we need to
        # download.
        keys = []
        if len(objs) > 20:
            last = sorted(objs, key=objs.get)[-20:]
        else:
            last = sorted(objs, key=objs.get)
        for key in last[::-1]:
            keys.append(key)
            if key.endswith(self.FULL_BACKUP_SUFFIX):
                break
        return keys

    # pylint: disable=no-self-use
    def _restore_influxdb_data(self, client):
        """ Helper function to restore influxdb data """
        databases = []
        for tarball_path in sorted(pathlib.Path('.').glob('**/*.tar.gz')):
            cmd = ['tar', 'xf', os.fspath(tarball_path)]
            logging.info(cmd)
            if not execute_cmd(cmd):
                return False

            influxdb_data_dir = os.fspath(tarball_path).strip('.tar.gz').split(
                '/')[1]
            if influxdb_data_dir.endswith('-full'):
                cmd = ['influxd', 'restore', '-portable', influxdb_data_dir]
                if not execute_cmd(cmd):
                    return False
                databases = [
                    _db['name'] for _db in client.get_list_database()
                    if _db['name'] != '_internal'
                ]
                logging.info('Databases: %s', ','.join(databases))
            elif influxdb_data_dir.endswith('-inc'):
                for dbname in databases:
                    inc_db = dbname + '_inc'
                    cmd = [
                        'influxd', 'restore', '-db', dbname, '-newdb', inc_db,
                        '-portable', influxdb_data_dir
                    ]
                    if not execute_cmd(cmd):
                        return False
                    client.switch_database(inc_db)
                    query = 'SELECT * INTO {}..:MEASUREMENT FROM /.*/ GROUP BY *'.format(
                        dbname)
                    try:
                        client.query(query, raise_errors=True)
                    except InfluxDBClientError as error:
                        if str(error) in [
                                'shard is disabled', 'engine is closed',
                                'query engine shutdown'
                        ]:
                            logging.info('Ignoring error: %s', error)
                        else:
                            raise
                    client.drop_database(inc_db)
            os.unlink(os.fspath(tarball_path))
        return True

    def restore_data(self):
        """ Restore from zinfluxdb data tarballs """
        username = os.environ.get('INFLUXDB_ADMIN_USER')
        password = os.environ.get('INFLUXDB_ADMIN_PASSWORD')

        if any(var is None for var in [username, password]):
            logging.error('Influxdb username/password cannot be None.')
            return False
        influxdb_client = InfluxDBClient(host=self.HOST,
                                         port=self.PORT,
                                         username=username,
                                         password=password,
                                         ssl=True,
                                         verify_ssl=False,
                                         database=None)
        dbs = influxdb_client.get_list_database()
        if dbs:
            for _db in dbs:
                if _db['name'] != '_internal':
                    logging.info('Dropping %s', _db['name'])
                    influxdb_client.drop_database(_db['name'])
        try:
            os.chdir(self.BACKUP_DIR)
        except OSError as error:
            logging.error('Unable to change directory to %s: %s',
                          self.BACKUP_DIR, error)
            return False

        return self._restore_influxdb_data(influxdb_client)


class CassandraData(DataSource):
    """ Cassandra Data Source """
    DATA_DIR = '/var/lib/cassandra'
    BACKUP_DIR = os.path.join(DATA_DIR, 'cassandra-data')
    KEYSPACE_REGEX = r'^schema-\w+.cql$'
    RESTRICTED_KEYSPACES = ['schema-system_schema.cql']

    HOST = '127.0.0.1'
    PORT = 9042

    def __init__(self, *args, **kwargs):
        self.datatype = CASSANDRA
        self.keyspaces_path = os.path.join(self.BACKUP_DIR, 'KEYSPACES')
        super().__init__(*args, **kwargs)

    # pylint: disable=no-self-use
    def get_last_backup_keys(self, objs):
        """ Return the set of last backups that comprise a full cassandra backup """
        # Assumption: the objects in the backup bucket are chronologically
        # ordered. We iterate over the last 20 objects in reverse order to find the last
        # full backup, while adding them to the list of blobs that we need to
        # download.
        keys = [os.path.dirname(bkp) for bkp in objs]
        data = {}
        for key in keys:
            data.update({
                key:
                datetime.strptime(key.split('/')[1],
                                  '%Y-%m-%d_%H-%M-%S').timestamp()
            })
        dirname = sorted(data, key=data.get)[-1]
        dbs = [
            'brazosdb', 'doloresdb', 'gangesdb', 'indusdb', 'purusdb',
            'seinedb', 'system_schema', 'tigrisdb', 'upgrade', 'vault',
            'volgadb'
        ]
        return ['{}/{}.tar.gz.gpg'.format(dirname, db) for db in dbs]

    def restore_keyspaces(self):
        """ Restore keyspaces """
        logging.info('Restoring keyspaces')
        try:
            os.chdir(self.BACKUP_DIR)
        except OSError as error:
            logging.error('Unable to change directory to %s: %s',
                          self.BACKUP_DIR, error)
            return False

        # Remove the KEYSPACES file if it exists
        if os.path.exists(self.keyspaces_path):
            os.unlink(self.keyspaces_path)

        # Find all the tarballs in the backup download directory
        for tarball_path in pathlib.Path('.').glob('*/*.tar.gz'):
            cmd = ['tar', 'xf', os.fspath(tarball_path)]
            logging.info(cmd)
            if not execute_cmd(cmd):
                return False
        logging.info('Untarring completed')

        # Restore the keyspace schemas
        keyspace_restore_cmd_prefix = [
            'cqlsh', '-u',
            os.getenv('CASSANDRA_USERNAME'), '-p',
            os.getenv('CASSANDRA_PASSWORD'), '-f'
        ]
        restored_keyspaces = []
        for schema_path in pathlib.Path('.').glob('schema-*.cql'):
            logging.info('Restoring schema from %s', schema_path)
            keyspace_schema = os.fspath(schema_path)
            if keyspace_schema in self.RESTRICTED_KEYSPACES or not re.match(
                    self.KEYSPACE_REGEX, keyspace_schema):
                logging.info('Skipping restoring %s', keyspace_schema)
                continue
            keyspace = keyspace_schema[len('schema-'):-len('.cql')]
            with open(self.keyspaces_path, 'a') as ksfh:
                ksfh.write('{}\n'.format(keyspace))
            cmd = keyspace_restore_cmd_prefix + [keyspace_schema]
            logging.info(cmd)
            if not execute_cmd(cmd):
                return False
            restored_keyspaces.append(keyspace)
        logging.info('Keyspaces restored: %s', ','.join(restored_keyspaces))
        return True

    def restore_data(self):
        """ Restore from cassandra data tarballs """
        try:
            os.chdir(self.BACKUP_DIR)
        except OSError as error:
            logging.error('Unable to change directory to %s: %s',
                          self.DATA_DIR, error)
            return False

        # Load the keyspaces from KEYSPACES file
        with open(self.keyspaces_path) as kpath:
            keyspaces = [key.strip('\n') for key in kpath.readlines()]
            kpath.close()
        keyspaces.append('system_schema')

        logging.info('Restoring data for %s', ','.join(keyspaces))
        for keyspace in keyspaces:
            for sdir in pathlib.Path(keyspace).glob('*/snapshots/backup-*'):
                spath = os.path.join(self.BACKUP_DIR, sdir)
                tbl_name = os.fspath(sdir).split('-')[0].split('/')[1]
                tdir_path = os.path.join(self.DATA_DIR, 'data', keyspace)
                tpath = list(pathlib.Path(tdir_path).glob(tbl_name + '-*'))[0]
                logging.info('Restoring %s/%s data', keyspace, tbl_name)
                for entry in os.listdir(spath):
                    try:
                        src = os.path.join(spath, entry)
                        dest = os.path.join(tpath, entry)
                        if os.path.isfile(src):
                            shutil.copy2(src, dest)
                    except OSError as error:
                        logging.error('Failed to copy %s -> %s: %s', src, dest,
                                      error)
                        return False
        logging.info('Restoring data DONE')
        return True

    def refresh_data(self):
        """ Refresh data """
        logging.info('Refreshing data')
        system_dir = os.path.join(self.DATA_DIR, 'data/system')
        shutil.rmtree(system_dir)
        os.makedirs(system_dir)
        repair_cmd = ['nodetool', 'repair']
        if not execute_cmd(repair_cmd):
            return False
        return True

    # pylint: disable=too-many-locals
    def verify_data(self):
        """ Verify restored data """
        logging.info('Verifying data')
        with open(self.keyspaces_path) as kpath:
            keyspaces = [key.strip('\n') for key in kpath.readlines()]
            kpath.close()

        if os.getenv('CASSANDRA_USERNAME') is None or os.getenv(
                'CASSANDRA_PASSWORD') is None:
            logging.error('Cassandra credentials are None')
            return False

        cluster = Cluster(contact_points=[self.HOST],
                          load_balancing_policy=DCAwareRoundRobinPolicy(
                              local_dc='datacenter1'),
                          port=self.PORT,
                          auth_provider=PlainTextAuthProvider(
                              username=os.getenv('CASSANDRA_USERNAME'),
                              password=os.getenv('CASSANDRA_PASSWORD')),
                          protocol_version=3,
                          ssl_options={'check_hostname': False})
        if not cluster:
            logging.error('Unable to connect to cassandra')
            return False

        logging.info('Verifying data for %s', ','.join(keyspaces))
        session = cluster.connect()
        try:
            for keyspace in keyspaces:
                path = os.path.join(self.BACKUP_DIR, keyspace + '.stats')
                with open(path) as stats:
                    for line in stats.readlines():
                        tbl, rows = line.split()
                        expected_rows = int(rows)
                        query = 'SELECT COUNT(*) FROM {};'.format(tbl)
                        try:
                            results = session.execute(query)
                            actual_rows = int(results.one().count)
                            if not row_count_ok(tbl, expected_rows,
                                                actual_rows):
                                logging.error(
                                    'Row count for %s differ too much (expected=%d, actual=%d)',
                                    tbl, expected_rows, actual_rows)
                            logging.info('%s OK', tbl)
                        except (OperationTimedOut, ReadFailure) as error:
                            logging.error('Failed to execute query: %s: %s',
                                          query, error)
                            return False
                    stats.close()
        except OSError as error:
            logging.error(error)
            return False
        session.shutdown()

        return True

    def cleanup(self):
        """ Cleanup """
        logging.info('Cleanup')
        try:
            shutil.rmtree(self.BACKUP_DIR)
        except OSError as error:
            logging.error('Cannot delete %s: %s', self.BACKUP_DIR, error)
            return False
        return True


class BackupClient(ABC):
    """ Generic backup client abstraction """
    def __init__(self, *args, **kwargs):  #pylint: disable=unused-argument
        self.datasource = None
        self.storage_client = None
        self.backups = {}
        self.idx = 0
        if 'datatype' not in kwargs:
            logging.error('Need datatype to initialize backup client.')
            sys.exit(1)
        datatype = kwargs['datatype']
        if datatype == ZINFLUXDB:
            self.datasource = InfluxData(*args, **kwargs)
        elif datatype == CASSANDRA:
            self.datasource = CassandraData(*args, **kwargs)
        else:
            logging.error('Unsupported datatype: %s', self.datasource.datatype)
            sys.exit(1)

    def __iter__(self):
        self.idx = 0
        return self

    def __next__(self):
        if self.idx < len(self.backups):
            item = self.backups[self.idx]
            self.idx += 1
            return item
        raise StopIteration

    def __len__(self):
        return len(self.backups)

    def __getitem__(self, idx):
        return self.backups[idx]

    def _download(self, path):
        """ Download the given path from storage backend """

    def get_last_backup_keys(self):
        """ Get last backups for the type of backup:
            - For cassandra, it would be paths to each db tarball (nilesdb.tar.gz,
              brazosdb.tar.gz etc)
            - For influxdb, it would be list of incremental backups till last
              full backup
            In both cases, the last backups will return a list of tarballs to be
            downloaded
        """
        return self.datasource.get_last_backup_keys(self.backups)

    def restore(self):
        """ Restore data from the tarballs """
        return self.datasource.restore()


class S3Client(BackupClient):
    """ S3 Client implementation """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            s3_resource = boto3.resource('s3')
            # pylint: disable=no-member
            self.backup_bucket = s3_resource.Bucket(
                os.environ['S3_BACKUP_BUCKET'])
        except ClientError as error:
            logging.error(error)
        self._get_backups()

    def _get_backups(self):
        """ Retrieve list of backups from the datasource """
        pfx = self.datasource.datatype + '-data'
        self.backups = {}
        for obj in self.backup_bucket.objects.filter(Prefix=pfx):
            self.backups.update({obj.key: obj.last_modified.timestamp()})

    def _download(self, path):
        """ Download encrypted blob at the path in S3 storage backend """
        backups = list(self.backup_bucket.objects.filter(Prefix=path))
        if not backups:
            logging.error('Backup %s not found.', path)
            return None

        assert len(backups) == 1
        blob = backups[0].key
        try:
            os.makedirs(os.path.dirname(blob))
        except OSError as error:
            if error.errno != errno.EEXIST:
                raise

        try:
            self.backup_bucket.download_file(blob, blob)
            logging.info('Downloaded %s (%d bytes)', blob,
                         os.path.getsize(blob))
        except ClientError as error:
            logging.error('Failed to download %s: %s', blob, error)
            return None
        return blob

    def download_last_backup(self):
        """ Download the last backups and return list of filenames """
        try:
            os.chdir(self.datasource.DATA_DIR)
        except OSError as error:
            logging.error('Unable to change directory to %s: %s',
                          self.datasource.DATA_DIR, error)
            return []
        keys = self.datasource.get_last_backup_keys(self.backups)
        return [self._download(key) for key in keys]


class AzureClient(BackupClient):
    """ Azure Client implementation """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.getLogger('azure').setLevel(logging.WARN)
        try:
            az_connection = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
            az_backup_container = os.environ.get('AZURE_BLOB_BACKUP_CONTAINER')
            blob_service_client = BlobServiceClient.from_connection_string(
                az_connection)
            self.storage_client = blob_service_client.get_container_client(
                az_backup_container)
        except ClientError as error:
            logging.error(error)
        self._get_backups()

    def _get_backups(self):
        """ Retrieve list of backups from the datasource """
        pfx = self.datasource.datatype + '-data'
        self.backups = {}
        for obj in self.storage_client.list_blobs(name_starts_with=pfx):
            self.backups.update({obj.name: obj.last_modified.timestamp()})

    def _download(self, path):
        """ Download encrypted blob from given path from Azure backend """
        backups = list(self.storage_client.list_blobs(name_starts_with=path))

        if not backups:
            logging.error('Backup %s not found.', path)
            return None

        assert len(backups) == 1
        blob = backups[0].name
        try:
            os.makedirs(os.path.dirname(blob))
        except OSError as error:
            if error.errno != errno.EEXIST:
                raise

        try:
            blob_client = self.storage_client.get_blob_client(blob)
            with open(blob, 'wb') as data:
                stream = blob_client.download_blob()
                data.write(stream.readall())
                data.close()
            logging.info('Downloaded %s (%d bytes)', blob,
                         os.path.getsize(blob))
        except ClientError as error:
            logging.error('Failed to download %s: %s', blob, error)
            return None
        return blob

    def download_last_backup(self):
        """ Download the last backups and return list of filenames """
        try:
            os.chdir(self.datasource.DATA_DIR)
        except OSError as error:
            logging.error('Unable to change directory to %s: %s',
                          self.datasource.DATA_DIR, error)
            return []
        keys = self.datasource.get_last_backup_keys(self.backups)
        return [self._download(key) for key in keys]


def get_backup_client(dbtype=None):
    """Determine if we are using AWS or Azure for backups and return a client
       for that """
    if all([env in os.environ for env in AWS_VARS]):
        return S3Client(datatype=dbtype)

    if all([env in os.environ for env in AZURE_VARS]):
        return AzureClient(datatype=dbtype)

    logging.error('Unknown backup strategy.')
    return None


def decrypt(blob):
    """ Decrypt the given blob with the passphrase in environment variable """
    logging.debug('Decrypting %s', blob)
    homedir = os.path.join(os.getenv('HOME'), '.gnupg')
    gpg = gnupg.GPG(gnupghome=homedir, keyring='pubring.kbx')
    public_keys = gpg.list_keys()
    if not public_keys:
        logging.error('No keys found!')
        return None
    if not os.path.exists(blob):
        logging.error('%s does not exist', blob)
        return None
    decrypted_tarball = blob[:-4] if blob[-4:] == '.gpg' else blob
    passphrase = os.getenv('GPG_PASSPHRASE')
    if not passphrase:
        logging.error('No key found in GPG_PASSPHRASE')
        return None
    try:
        with open(blob, 'rb') as output:
            status = gpg.decrypt_file(output,
                                      passphrase=passphrase,
                                      output=decrypted_tarball)
            output.close()
            if status.ok:
                return decrypted_tarball
    except OSError as error:
        logging.error(error)
    return None


# pylint: disable=too-many-return-statements,too-many-branches
def restore(dbtype, params):
    """ Restore data """
    client = get_backup_client(dbtype)
    if params.show_last:
        print('\n'.join(client.get_last_backup_keys()))
        return 0

    if params.download:
        encrypted_tarballs = client.download_last_backup()
        for etarball in encrypted_tarballs:
            if not os.path.exists(etarball):
                logging.error('%s does not exist', etarball)
                return 1
            if not decrypt(etarball):
                logging.error('Failed to decrypt %s', etarball)
                return 1
        return 0

    if params.restore_keyspaces:
        if not client.datasource.restore_keyspaces():
            logging.error('Failed to restore keyspaces.')
            return 1
    elif params.restore:
        if not client.datasource.restore_data():
            logging.error('Failed to restore %s data.',
                          client.datasource.datatype)
            return 1
    elif params.refresh:
        if not client.datasource.refresh_data():
            logging.error('Failed to refresh keyspaces.')
            return 1
    elif params.verify:
        if not client.datasource.verify_data():
            logging.error('Failed to verify restored data.')
            return 1
        if not client.datasource.cleanup():
            logging.error('Failed to cleanup temporary files.')
            return 1
    else:
        logging.error('Unsupported action')
    return 0


# pylint: disable=too-many-branches
def main():
    """ Main """
    parser = argparse.ArgumentParser('restore')
    parser.add_argument('--debug',
                        action='store_true',
                        help='Set log level to debug')
    parser.add_argument('--verbose',
                        action='store_true',
                        help='Set log level to verbose')
    parser.add_argument('--show-last',
                        action='store_true',
                        help='Show the last available backup')
    parser.add_argument('--download',
                        action='store_true',
                        help='Download last backup specified or as specified')
    parser.add_argument('--restore', action='store_true', help='Restore data.')
    parser.add_argument('--restore-keyspaces',
                        action='store_true',
                        help='Restore keyspaces (cassandra only).')
    parser.add_argument('--refresh',
                        action='store_true',
                        help='Refresh keyspaces (cassandra only).')
    parser.add_argument('--verify',
                        action='store_true',
                        help='Verify restored data (cassandra only).')
    params, dbargs = parser.parse_known_args()

    # Logging
    log_level = logging.ERROR
    if params.debug:
        log_level = logging.DEBUG
    elif params.verbose:
        log_level = logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)s %(message)s')
    urllib3.disable_warnings()

    # DB validation
    if not dbargs:
        logging.error('Need DB type to restore.')
        sys.exit(1)
    if dbargs[0] not in SUPPORTED_DBS:
        logging.error('Sorry, restoring %s data not supported as yet.',
                      dbargs[0])
        sys.exit(1)
    if dbargs[0] != CASSANDRA:
        if params.restore_keyspaces or params.refresh or params.verify:
            logging.error('--restore-keyspaces, --refresh and --verify only '
                          'available for Cassandra.')
            sys.exit(1)

    return restore(dbargs[0], params)


if __name__ == '__main__':
    sys.exit(main())
