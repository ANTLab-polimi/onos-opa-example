# onos-opa-example

Intent Monitor and Reroute (IMR) service offers ONOS applications and users the possibility to expose statistics and re-routing capabilities, of specific intents, to external Off-Platform Application (OPA).

The OPA can re-route those monitored intents based on the collected flow level statistics optimizing a global network objective.

IMR requires little code modification to the ONOS application that wants to take advantage of the OPA: it doesn't affect the way the application submits intents to the Intent Framework, IMR only needs to be aware of which intents the ONOS application wants to expose to the OPA and then it will automatically collect statistics and re-route intents.

# Tutorial

This repository contains an example of a possible OPA logic to be interconnected with the IMR service.

The onos repository contains ONOS plus Intent Monitor and Reroute (IMR) service and Intent Reactive Forwarding (IFWD) application.

Clone both repository in your home directory
```bash
$ cd ~
$ git clone -b imr https://github.com/ANTLab-polimi/onos.git
$ git clone https://github.com/ANTLab-polimi/onos-opa-example.git
```

Configure your ~/.bashrc file by adding

```bash
export ONOS_ROOT=~/onos
source $ONOS_ROOT/tools/dev/bash_profile
```

and source it
```bash
$ source ~/.bashrc
```

Now build ONOS with the following command
```bash
$ $ONOS_ROOT/tools/build/onos-buck run onos-local -- clean debug
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
From the GUI http://localhost:8181/onos/ui/index.html we can verify that the IFWD appilcation established connectivity using shortest paths by pressing (A) key.

Without modifying the IFWD application we can now ask the monitoring and rerouting of all the intents it has submitted
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

While OPA is able to reroute intents via IMR, it does not limit the effectiveness of the Intent Framework in recovering from failues.
```bash
mininet> sh ifconfig s1-eth down
```

# REST API endpoints and JSON Format

TODO
