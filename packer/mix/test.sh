cat << EOF > /usr/users.txt
s5idriss
EOF
username=$(cat /usr/users.txt | tr '[A-Z]' '[a-z]')
function user_add() {
    for users in $username
    do
        ls /home |grep -w $users &>/dev/nul || mkdir -p /home/$users
        cat /etc/passwd |awk -F: '{print$1}' |grep -w $users &>/dev/nul ||  useradd $users
        chown -R $users:$users /home/$users
        cd /home/$users && git clone https://github.com/devopseasylearning/SESSION-01-DEVELOPMENT.git || true
        usermod -s /bin/bash -aG student $users
        echo -e "$users\n$users" |passwd "$users"
    done
}
