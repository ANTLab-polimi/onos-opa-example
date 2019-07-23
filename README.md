# onos-opa-example
Intent Monitor and Reroute (IMR) service offers ONOS applications and users the possibility to expose statistics and re-routing capabilities, of specific intents, to external Off-Platform Application (OPA).
The OPA can re-route those monitored intents based on the collected flow level statistics optimizing a global network objective.


IMR requires little code modification to the ONOS application that wants to take advantage of the OPA: it doesn't affect the way the application submits intents to the Intent Framework, IMR only needs to be aware of which intents the ONOS application wants to expose to the OPA and then it will automatically collect statistics and re-route intents.

This repository contains an example of a possible Off-Platform Application (OPA) logic to be interconnected with the new Intent Monitor and Reroute (IMR) service.
In this tutorial we are going to create a simple topology and two pairs of intents using the Intent Reactive Forwarding (IFWD) application. We'll then require the IMR service to monitor their statistics and to expose the data to the OPA which in turn will re-reroute the paths.

## Publications
* D. Sanvito, D. Moro, M. Gullì, I. Filippini, A. Capone and A. Campanella, "ONOS Intent Monitor and Reroute service: enabling plug&play routing logic," 2018 4th IEEE Conference on Network Softwarization and Workshops (NetSoft), 2018. [Paper available at IEEE Xplore](https://ieeexplore.ieee.org/abstract/document/8460064)
* D. Sanvito, D. Moro, M. Gullì, I. Filippini, A. Capone and A. Campanella, "Enabling external routing logic in ONOS with Intent Monitor and Reroute service," 2018 4th IEEE Conference on Network Softwarization and Workshops (NetSoft), 2018. [Poster](https://davidesanvito.github.io/pub/2018-06-netsoft-poster.pdf)

## Pre-requisites

This tutorial requires an Ubuntu 16.04.3 (64 bit) Server distribution: we suggest a dedicated VM with 4-8 GB of RAM and 20 GB of storage.
If you already have a working ONOS installation on your machine, you can jump to the “Download IMR service” step, otherwise keep following these instructions.

You can manually install all the pre-requisites or just run an automatic script  and then jump right to "Tutorial" section.

### Automatic installation (recommended)
```
bash -c "$(wget -O - https://git.io/vAPer)"
source ~/.bashrc
```

### Manual installation

Open a terminal and install Java 8
```
sudo apt-get update && \
sudo apt-get install git python python-pip python-matplotlib curl unzip zip software-properties-common -y && \
sudo add-apt-repository ppa:webupd8team/java -y && \
sudo apt-get update && \
echo "oracle-java8-installer shared/accepted-oracle-license-v1-1 select true" | sudo debconf-set-selections && \
sudo apt-get install oracle-java8-installer oracle-java8-set-default -y
sudo apt-get install python-minimal openjdk-8-jdk -y
```
Install Apache Maven 3.3.9
```
cd /usr/local
sudo wget http://archive.apache.org/dist/maven/maven-3/3.3.9/binaries/apache-maven-3.3.9-bin.tar.gz
sudo tar xzf apache-maven-3.3.9-bin.tar.gz
echo "export M2_HOME=/usr/local/apache-maven-3.3.9/" >> ~/.bashrc
echo "export MAVEN_HOME=/usr/local/apache-maven-3.3.9/" >> ~/.bashrc
echo "export PATH=\${M2_HOME}/bin:${PATH}" >> ~/.bashrc
source ~/.bashrc
sudo rm -f apache-maven-3.3.9-bin.tar.gz
```

Install Mininet
```
cd --
git clone git://github.com/mininet/mininet
sudo mininet/util/install.sh -a
```

Install Bazel
```
cd --
sudo apt-get install pkg-config zip g++ zlib1g-dev unzip python3 -y
wget https://github.com/bazelbuild/bazel/releases/download/0.23.2/bazel-0.23.2-installer-linux-x86_64.sh
chmod +x bazel-0.23.2-installer-linux-x86_64.sh
./bazel-0.23.2-installer-linux-x86_64.sh --user
echo "export PATH=\"$PATH:$HOME/bin\"" >> ~/.bashrc
```

Clone the onos repository

NB IMR is guaranteed to be supported by ONOS v1.15 up to commit 3bc7060466c0d0da72799455ac2eb44048e1bd3d
```
cd --
git clone https://gerrit.onosproject.org/onos 
cd onos
git reset --hard 3bc7060466c0d0da72799455ac2eb44048e1bd3d

echo "export ONOS_ROOT=~/onos" >> ~/.bashrc
echo  "source \$ONOS_ROOT/tools/dev/bash_profile" >> ~/.bashrc
source ~/.bashrc
```
Build ONOS

```
cd $ONOS_ROOT
bazel build onos
```

Download and install IFWD application

NB IMR currently supports only LinkCollectionIntent and PointToPointIntent.
We provide a modified IFWD application which sumits PointToPointIntents instead of HostToHostIntents.
```
cd --
git clone -b ifwd-p2p-intents https://github.com/ANTLab-polimi/onos-app-samples
cd onos-app-samples/ifwd
mvn clean install
```

Download the example OPA
```
cd --
git clone https://github.com/ANTLab-polimi/onos-opa-example.git
cd onos-opa-example
sudo pip install -r requirements.txt
```

Patch IMR to submit PointToPointIntent with suggested path instead of LinkCollectionIntent. This step is required because Gerrit Patch #16569 was not integrated in ONOS when IMR was originally included.

```
cd $ONOS_ROOT
git apply ../onos-opa-example/misc/imr-submits-p2pintent-suggested-path.patch
```

## Tutorial

Start ONOS controller
```
cd $ONOS_ROOT
bazel run onos-local -- clean debug
```
Once ONOS is ready, from another terminal deactivate the FWD application and enable IMR service
```
cd ~/onos-app-samples
onos-app localhost deactivate org.onosproject.fwd
onos-app localhost activate org.onosproject.imr
```
Then install and activate IFWD application
```
onos-app localhost install! ./ifwd/target/onos-app-ifwd-1.9.0-SNAPSHOT.oar
```
Create a simple Mininet topology
```
cd ~/onos-opa-example/topo
sudo python topo.py
```
Let's start 2 iperf sessions from h1 to h3 and from h2 to h4.
```
mininet> h3 iperf -s &
mininet> h4 iperf -s &
mininet> h1 iperf -c 10.0.0.3 -t 600 &
mininet> h2 iperf -c 10.0.0.4 -t 600 &
```
Connect to the GUI at http://[VM_IP]:8181/onos/ui/index.html (credentials are onos/rocks) and verify that the IFWD application established connectivity using shortest paths by pressing (A) key.

<img src="https://raw.githubusercontent.com/ANTLab-polimi/onos-opa-example/master/img/1.png" width="500">

Without modifying the IFWD application, we can now require the monitoring and rerouting of all the intents it has submitted using the following CLI command from another terminal. (The appID value might differ from 161, but you can use the Tab Key to autocomplete CLI commands)
```
onos localhost
onos> imr:startmon 161 org.onosproject.ifwd
onos> logout
```
Finally we can start the OPA
```
cd ~/onos-opa-example
python main_one_shot.py
```

The rerouting logic is a simple greedy algorithm which collects one Traffic Matrix (TM) and iteratively select for each demand (sorted in descending order) the shortest path on the capacitated residual graph.
From the GUI we can verify that, after 2 polling cycles, OPA has modified the routings. Some intents has been relocated and this improves the performance of the 2 iperf sessions.

<img src="https://raw.githubusercontent.com/ANTLab-polimi/onos-opa-example/master/img/2.png" width="500">

While OPA is able to reroute intents via IMR, it does not limit the effectiveness of the Intent Framework in recovering from failures.
```
mininet> sh ifconfig s1-eth1 down
```

### Tutorial (2)

The implemented approach can be iterated to periodically collect TM data and re-optimize the paths which realize the application intents.

The full OPA application collects TM data for 3 polling cycles, builds the worst case TM (by keeping for each demand its worst-case value in the latest training interval) and finally iteratively select for each demand (sorted in descending order) the shortest path on the capacitated residual graph.


```bash
$ cd ~/onos-opa-example
$ python main.py
```

The polling period and the number of TMs to be collected before applying the greedy algorithm can be configured in ```config.py``` file.

# CLI API

IMR service adds two CLI commands to start/stop the monitoring of all the intents (or a specific one) submitted by an application.

```bash
onos> imr:startmon [--longkey] appId appName [intentKey]
onos> imr:stopmon [--longkey] appId appName [intentKey]
```
If the optional intentKey argument is omitted, all the intents currently submitted by the application will be monitored/unmonitored.
The optional --longkey (--l) specifies that intentKey should be treated as LongKey rather than StringKey.

# REST API endpoints and JSON Format

IMR service and OPA can communicate via a REST API.
There are three main endpoints.
The first one allows to retrieve, via an HTTP GET, the statistics of all the monitored intents from any application or from a specific application or of a specific monitored intent.
```
http://localhost:8181/onos/v1/imr/imr/intentStats
http://localhost:8181/onos/v1/imr/imr/intentStats/appId/appName
http://localhost:8181/onos/v1/imr/imr/intentStats/appId/appName/intentKey
```
The body of the reply is a JSON message with the following format:
```json
{  
    "statistics":[  
        {  
            "id":109,
            "name":"org.onosproject.ifwd",
            "intents":[  
                {  
                    "00:00:00:00:00:01/None00:00:00:00:00:02/None":[  
                        {  
                            "id":"45035999039801587",
                            "tableId":0,
                            "appId":"org.onosproject.net.intent",
                            "groupId":0,
                            "priority":100,
                            "timeout":0,
                            "isPermanent":true,
                            "deviceId":"of:0000000000000001",
                            "state":"ADDED",
                            "life":56,
                            "packets":0,
                            "bytes":0,
                            "liveType":"UNKNOWN",
                            "lastSeen":1513696955188,
                            "treatment":{  
                                "instructions":[  
                                    {  
                                        "type":"OUTPUT",
                                        "port":"4"
                                    }
                                ],
                                "deferred":[  

                                ]
                            },
                            "selector":{  
                                "criteria":[  
                                    {  
                                        "type":"IN_PORT",
                                        "port":3
                                    },
                                    {  
                                        "type":"ETH_DST",
                                        "mac":"00:00:00:00:00:02"
                                    },
                                    {  
                                        "type":"ETH_SRC",
                                        "mac":"00:00:00:00:00:01"
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
    ]
}
```

The second one allows to retrieve, via an HTTP GET, the element ids of the endpoints of all the monitored intents from any application or from a specific application or of a specific monitored intent.
```
http://localhost:8181/onos/v1/imr/imr/monitoredIntents
http://localhost:8181/onos/v1/imr/imr/monitoredIntents/appId/appName
http://localhost:8181/onos/v1/imr/imr/monitoredIntents/appId/appName/intentKey
```
The body of the reply is a JSON message with the following format:
```
{  
    "response":[  
        {  
            "id":109,
            "name":"org.onosproject.ifwd",
            "intents":[  
                {  
                    "key":"00:00:00:00:00:01/None00:00:00:00:00:02/None",
                    "inElements":[  
                        "00:00:00:00:00:01/None"
                    ],
                    "outElements":[  
                        "00:00:00:00:00:02/None"
                    ]
                }
            ]
        }
    ]
}
```

The last one allows to enforce, via an HTTP POST, for a specific set of intents a corresponding weighted set of paths, where each path is an ordered sequence of element ids.
```
http://localhost:8181/onos/v1/imr/imr/reRouteIntents
```
The body of the request is a JSON message with the following format:
```
{  
    "routingList":[  
        {  
            "appId":{  
                "id":109,
                "name":"org.onosproject.ifwd"
            },
            "key":"00:00:00:00:00:01/None00:00:00:00:00:03/None",
            "paths":[  
                {  
                    "path":[  
                        "00:00:00:00:00:01/None",
                        "of:0000000000000001",
                        "of:0000000000000002",
                        "00:00:00:00:00:03/None"
                    ],
                    "weight":1.0
                }
            ]
        }
    ]
}
```

