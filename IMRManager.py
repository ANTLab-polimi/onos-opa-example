import json

from config import ONOS_IP, ONOS_PORT
from utils import json_get_req, json_post_req


class IMRManager ():
    def __init__(self, topology):
        self.intents = {}
        self.topology = topology

        # device's id is 'of:00000000000000a1', device's chassisID is 'a1'
        reply = json_get_req("http://%s:%d/onos/v1/imr/monitoredIntents" % (ONOS_IP, ONOS_PORT))
        if 'response' not in reply:
            return
        for intent in reply['response']:
            key = intent['key']
            del intent['key']
            self.intents[key] = intent



    def reRouteMonitoredIntents(self):
        reRouting = {"routingList" : []}
        i = 0
        for (key, intent) in self.intents.items():
            path = self.topology.shortestPath(intent['inElement'], intent['outElement'])
            current_reroute = {}
            current_reroute["key"] = key
            current_reroute["appId"] = {}
            current_reroute["appId"]["id"] = intent["appId"]
            current_reroute["appId"]["name"] = intent['appName']
            current_reroute["paths"] = []
            current_reroute["paths"].append({})
            current_reroute["paths"][0]["path"] = path
            current_reroute["paths"][0]["weight"] = 1.0
            reRouting["routingList"].append(current_reroute)
            i += 1
        print "ReRouting config:"
        print reRouting
        json_post_req(("http://%s:%d/onos/v1/imr/reRouteIntents" % (ONOS_IP, ONOS_PORT)), json.dumps(reRouting))

