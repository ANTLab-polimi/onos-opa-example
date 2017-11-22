import threading
import time
from IMRManager import IMRManager
from StatsManager import StatsManager
from TopoManager import TopoManager
'''from IMRManager import FakeIMRManager as IMRManager
from StatsManager import FakeStatsManager as StatsManager
from TopoManager import FakeTopoManager as TopoManager'''
from config import POLLING_INTERVAL

topo = TopoManager()

statsManager = StatsManager()
while len(statsManager.get_TMs()) < 2:
    print 'Polling Intent stats...'
    threading.Thread(target=statsManager.poll_stats).start()
    time.sleep(POLLING_INTERVAL)

imrManager = IMRManager(topo)

if set(sum([TM.keys() for TM in statsManager.get_TMs()], [])) != imrManager.monitoredIntents():
    print 'Some TM samples related to intents excluded from monitoring during TM collection will be neglected!'

# Build the TMs keeping only intentKeys related to intents currently monitored and considering the worst-case demand value
worst_TM = {intentKey: max([TM[intentKey] if intentKey in TM else 0 for TM in statsManager.get_TMs()])
            for intentKey in imrManager.monitoredIntents()}

print 'worst_TM', worst_TM
imrManager.reRouteMonitoredIntents(worst_TM)
