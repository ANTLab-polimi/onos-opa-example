import threading
import time
from IMRManager import IMRManager
from StatsManager import StatsManager
from TopoManager import TopoManager
from config import POLLING_INTERVAL, TM_TRAINING_SET_SIZE
from utils import bps_to_human_string

'''
from IMRManager import FakeIMRManager as IMRManager
from StatsManager import FakeStatsManager as StatsManager
from TopoManager import FakeTopoManager as TopoManager
'''

# TODO create pip requirements.txt file
# TODO adapt FakeManagers for the new REST API

topo = TopoManager()
# topo.draw_topo()

statsManager = StatsManager()
while len(statsManager.get_tm_store()) <= TM_TRAINING_SET_SIZE:
    print 'Polling Intent stats...'
    threading.Thread(target=statsManager.poll_stats).start()
    time.sleep(POLLING_INTERVAL)

imrManager = IMRManager(topo)

if set(sum([tm.keys() for tm in statsManager.get_tm_store()], [])) != imrManager.get_monitored_intents():
    print 'Some tm samples, related to intents which are no longer monitored, have been ignored...'

# Build the worst case Traffic Matrix by keeping only demands whose intentKeys are currently monitored and considering
# their worst-case historical value
worst_tm = {intentKey: max([tm[intentKey] if intentKey in tm else 0 for tm in statsManager.get_tm_store()])
            for intentKey in imrManager.get_monitored_intents()}

print 'worst_tm', {flow_id: bps_to_human_string(worst_tm[flow_id]) for flow_id in worst_tm}
imrManager.reroute_monitored_intents(worst_tm)
