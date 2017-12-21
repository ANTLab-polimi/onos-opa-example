# Exit immediately if a command exits with a non-zero status.
set -e

# Exit immediately if a command tries to use an unset variable
set -o nounset

function install-prereq {
    sudo apt-get install -y python-pip python-matplotlib curl unzip zip
    sudo apt-get install software-properties-common -y
    sudo add-apt-repository ppa:webupd8team/java -y
    sudo apt-get update
    echo "oracle-java8-installer shared/accepted-oracle-license-v1-1 select true" | sudo debconf-set-selections
    sudo apt-get install oracle-java8-installer oracle-java8-set-default -y
}

function download-onos {
    cd ~
    rm -rf onos
    git clone -b imr https://github.com/ANTLab-polimi/onos.git
    echo "export ONOS_ROOT=~/onos" >> ~/.bashrc
    echo  "source \$ONOS_ROOT/tools/dev/bash_profile" >> ~/.bashrc
    echo  "export JAVA_TOOL_OPTIONS=-Dfile.encoding=UTF8" >> ~/.bashrc
}

function download-onos-opa {
    cd ~
    git clone https://github.com/ANTLab-polimi/onos-opa-example.git
    cd ~/onos-opa-example
    sudo pip install -r requirements.txt
}

sudo apt-get update
install-prereq
download-onos
download-onos-opa

echo "All set!"
