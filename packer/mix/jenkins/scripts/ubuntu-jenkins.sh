# sudo add-apt-repository ppa:openjdk-r/ppa
# sudo apt-get update
# sudo apt install unzip -y
# sudo apt-get install -y openjdk-8-jdk

# wget -q -O - https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo apt-key add -
# echo deb https://pkg.jenkins.io/debian-stable binary/ | sudo tee /etc/apt/sources.list.d/jenkins.list
# sudo apt-get update
# sudo apt-get install -y jenkins
# sudo systemctl start jenkins

sudo apt-get update
apt install wget -y
sudo apt install openjdk-11-jdk -y
wget -q -O - https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo apt-key add -
sudo sh -c 'echo deb https://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
sudo apt-get update
sudo apt-get install jenkins -y
sudo apt install git -y
# sudo systemctl start jenkins
# sudo systemctl status jenkins