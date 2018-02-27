#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Exit immediately if a command tries to use an unset variable
set -o nounset

function install-prereq {
    # Install Java
    sudo apt-get update && \
    sudo apt-get install git python python-pip python-matplotlib curl unzip zip software-properties-common -y && \
    sudo add-apt-repository ppa:webupd8team/java -y && \
    sudo apt-get update && \
    echo "oracle-java8-installer shared/accepted-oracle-license-v1-1 select true" | sudo debconf-set-selections && \
    sudo apt-get install oracle-java8-installer oracle-java8-set-default -y

    # Install Maven 3.3.9
    cd /usr/local
    sudo wget http://archive.apache.org/dist/maven/maven-3/3.3.9/binaries/apache-maven-3.3.9-bin.tar.gz
    sudo tar xzf apache-maven-3.3.9-bin.tar.gz
    echo "export M2_HOME=/usr/local/apache-maven-3.3.9/" >> ~/.sfile
    echo "export MAVEN_HOME=/usr/local/apache-maven-3.3.9/" >> ~/.sfile
    echo "export PATH=\${M2_HOME}/bin:${PATH}" >> ~/.sfile
    source ~/.sfile
    sudo rm -f apache-maven-3.3.9-bin.tar.gz

    # Install Mininet
    cd --
    git clone git://github.com/mininet/mininet
    sudo mininet/util/install.sh -a
}

function download-onos {
    # Download ONOS
    cd --
    git clone https://gerrit.onosproject.org/onos 
    echo "export ONOS_ROOT=~/onos" >> ~/.sfile
    source ~/.sfile

    # Download ONOS IMR service
    cd $ONOS_ROOT
    git fetch https://gerrit.onosproject.org/onos refs/changes/34/16234/7 && git checkout FETCH_HEAD
}

function download-onos-ifwd {
    cd --
    git clone -b ifwd-p2p-intents https://github.com/ANTLab-polimi/onos-app-samples
    cd onos-app-samples/ifwd
    mvn clean install
}

function download-onos-opa {
    cd --
    git clone https://github.com/ANTLab-polimi/onos-opa-example.git
    cd onos-opa-example
    export LC_ALL=C
    sudo pip install -r requirements.txt
    # Patching ONOS's PointToPointIntent to include suggested paths
    cd $ONOS_ROOT
    git apply ../onos-opa-example/misc/p2pintent-suggested-path.patch
}

install-prereq
download-onos
download-onos-ifwd
download-onos-opa

echo  "source \${ONOS_ROOT}/tools/dev/bash_profile" >> ~/.sfile
cat ~/.sfile >> ~/.bashrc
rm ~/.sfile

echo "Ready!"