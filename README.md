# onos-opa-example

Intent Monitor and Reroute (IMR) service offers ONOS applications and users the possibility to expose statistics and re-routing capabilities, of specific intents, to external Off-Platform Application (OPA).

The OPA can re-route those monitored intents based on the collected flow level statistics optimizing a global network objective.

IMR requires little code modification to the ONOS application that wants to take advantage of the OPA: it doesn't affect the way the application submits intents to the Intent Framework, IMR only needs to be aware of which intents the ONOS application wants to expose to the OPA and then it will automatically collect statistics and re-route intents.

# Install guide
This repository contains an example of a possible OPA logic to be interconnected with the IMR service, while the ```onos``` repository contains, in addition to ONOS, the new Intent Monitor and Reroute (IMR) service and Intent Reactive Forwarding (IFWD) application.

## Pre-requisites
Download Virtual Box and import the pre-configured VM at [link](https://bit.ly/onos-imr).

As an alternative, you can manually install Mininet 2.2.2 on Ubuntu (64 bit) and run the following command to install the pre-requisites and clone the repositories:
```bash
$ bash -c "$(wget -O - https://git.io/vbDqO)"
$ source ~/.bashrc
```
## Tutorial
Now with the VM just configured, you can build ONOS with the following command
```bash
$ cd $ONOS_ROOT
$ tools/build/onos-buck run onos-local -- clean debug
```
From another terminal we create a small Mininet topology
```bash
$ cd ~/onos-opa-example/topo
$ sudo python topo.py
```
From another terminal let's connect to the ONOS CLI to disable the Reactive Forwarding application and to enable Intent Reactive Forwarding and Intent Monitor And Reroute applications
```bash
$ onos localhost
onos> app deactivate org.onosproject.fwd
onos> app activate org.onosproject.ifwd org.onosproject.imr
```
Let's start 2 iperf sessions from h1 to h3 and from h2 to h4.
```bash
mininet> h3 iperf -s &
mininet> h4 iperf -s &
mininet> h1 iperf -c 10.0.0.3 -t 600 &
mininet> h2 iperf -c 10.0.0.4 -t 600 &
```
Connect to the GUI at http://[VM_IP]:8181/onos/ui/index.html (credentials are onos/rocks) and verify that the IFWD appilcation established connectivity using shortest paths by pressing (A) key.

<img src="https://raw.githubusercontent.com/ANTLab-polimi/onos-opa-example/master/img/1.png" width="500">

Without modifying the IFWD application we can now ask the monitoring and rerouting of all the intents it has submitted.
(The appID value might differ from 109, but you can use the  Tab Key to autocomplete CLI commands)
```bash
onos> imr:startmon 109 org.onosproject.ifwd
```
Finally we can start the OPA:
```bash
$ cd ~/onos-opa-example
$ python main.py
```
The rerouting logic is a simple greedy algorithm which collect TM data for 3 polling cycles, builds the worst case TM (by keeping for each demand its worst-case value in the latest training interval) and finally iteratively select for each demand (sorted in descending order) the shortest path on the capacitated residual graph.

From the GUI we can verify that, after 3 polling cycles, OPA has modified the routings.
Some intents has been relocated and this improves the performance of the 2 iperf sessions.

<img src="https://raw.githubusercontent.com/ANTLab-polimi/onos-opa-example/master/img/2.png" width="500">

While OPA is able to reroute intents via IMR, it does not limit the effectiveness of the Intent Framework in recovering from failues.
```bash
mininet> sh ifconfig s1-eth1 down
```
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
