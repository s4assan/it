https://dev.azure.com/

https://dev.azure.com/tialeo

https://www.youtube.com/watch?v=Nu33FKoGyWY&list=PLaFzfwmPR7_Ifxq-udm66fhReFeGOe2x_&index=4


Self Hosted private Agent on Linux (Ubuntu) for Azure Pipelines
https://www.youtube.com/watch?v=psa8xfJ0-zI


## Set up azure agent
https://www.youtube.com/watch?v=Hy6fne9oQJM
https://www.coachdevops.com/2023/01/how-to-setup-self-hosted-linux-agent-in.html
```
wget http://security.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2.17_amd64.deb
sudo dpkg -i libssl1.1_1.1.1f-1ubuntu2.17_amd64.deb
rm libssl1.1_1.1.1f-1ubuntu2.17_amd64.deb
sudo sed -i 's/openssl_conf = openssl_init/#openssl_conf = openssl_init/g' /etc/ssl/openssl.cnf


wget https://vstsagentpackage.azureedge.net/agent/2.214.1/vsts-agent-linux-x64-2.214.1.tar.gz
tar zxvf vsts-agent-linux-x64-2.214.1.tar.gz
./config.sh
sudo ./svc.sh install &
sudo ./runsvc.sh &
```

## Pipeline steps
https://aka.ms/yaml