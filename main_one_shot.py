import time
from IMRManager import IMRManager
from StatsManager import StatsManager
from TopoManager import TopoManager
from config import POLLING_INTERVAL

if __name__ == "__main__":
    # Initialize Topo Manger and get the latest version of the topology
    topoManager = TopoManager()

    # Initialize IMR Manger and get the latest set of monitored events
    imrManager = IMRManager()

    # Initialize Statistics Manager
    statsManager = StatsManager()
    # Poll ONOS's flow stats twice to build a Traffic Matrix
    statsManager.poll_stats()
    time.sleep(POLLING_INTERVAL)
    statsManager.poll_stats()

    latest_TM = statsManager.get_tm_store()[-1]
    imrManager.reroute_monitored_intents(latest_TM, topoManager)
