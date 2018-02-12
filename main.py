import threading
import time
from IMRManager import IMRManager
from StatsManager import StatsManager
from TopoManager import TopoManager
from config import POLLING_INTERVAL, TM_TRAINING_SET_SIZE, VERBOSE
from utils import bps_to_human_string
from pprint import pprint
import logging
import signal
import sys


class PollingThread(threading.Thread):
    def __init__(self):
        self._stopevent = threading.Event()
        threading.Thread.__init__(self)

    def run(self):
        while not self._stopevent.isSet():
            # Re-route intents as soon as TM_TRAINING_SET_SIZE TMs have been collected
            if len(statsManager.get_tm_store()) > 0 and len(statsManager.get_tm_store()) % TM_TRAINING_SET_SIZE == 0:
                reroute_event.set()
            threading.Thread(target=statsManager.poll_stats).start()
            time.sleep(POLLING_INTERVAL)

    def stop(self):
        self._stopevent.set()


class ReroutingThread(threading.Thread):
    def __init__(self):
        self._stopevent = threading.Event()
        threading.Thread.__init__(self)

    def run(self):
        while not self._stopevent.isSet():
            reroute_event.wait()
            if self._stopevent.isSet():
                return

            logging.info("Re-routing Intents...")
            reroute_event.clear()

            # Get the latest version of topology and monitored events
            imrManager.retrieve_monitored_intents_from_ONOS()
            topoManager.retrieve_topo_from_ONOS()

            # Build the worst case Traffic Matrix by keeping only demands whose intentKeys are still monitored and
            # considering their worst-case historical value of the latest training interval
            tm_list = statsManager.get_tm_store()[-TM_TRAINING_SET_SIZE:]
            monitored_intents = imrManager.get_monitored_intents()
            worst_tm = {intentKey: max([tm[intentKey] if intentKey in tm else 0 for tm in tm_list])
                        for intentKey in monitored_intents}

            if set(sum([tm.keys() for tm in tm_list], [])) != monitored_intents:
                if VERBOSE:
                    print 'Some tm samples, related to intents which are no longer monitored, have been ignored...'

            if VERBOSE:
                print 'worst_tm'
                pprint({flow_id: bps_to_human_string(worst_tm[flow_id]) for flow_id in worst_tm})

            imrManager.reroute_monitored_intents(worst_tm, topoManager)

    def stop(self):
        self._stopevent.set()
        reroute_event.set()

def handler_stop_signals(signum, frame):
    pollingThread.stop()
    reroutingThread.stop()
    logging.info('Killing all the threads...')
    sys.exit(0)

if __name__ == "__main__":
    topoManager = TopoManager()
    # topoManager.draw_topo()
    statsManager = StatsManager()
    imrManager = IMRManager()

    reroute_event = threading.Event()

    pollingThread = PollingThread()
    reroutingThread = ReroutingThread()
    pollingThread.start()
    reroutingThread.start()

    signal.signal(signal.SIGINT, handler_stop_signals)

    logging.info('Press any key to exit')
    raw_input('')
    logging.info('Killing all the threads...')
    pollingThread.stop()
    reroutingThread.stop()
