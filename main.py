from IMRManager import IMRManager
from TopoManager import FakeTopoManager as TopoManager
from StatsManager import FakeStatsManager as StatsManager
from config import POLLING_INTERVAL
import time
import threading


topo = TopoManager()

statsManager = StatsManager()
while len(statsManager.TMs) < 4:
    print 'Polling Intent stats...'
    threading.Thread(target=statsManager.get_TM_samples).start()
    time.sleep(POLLING_INTERVAL)

imrManager = IMRManager(topo)

TMs = statsManager.TMs
if set(sum([TM.keys() for TM in TMs], [])) != imrManager.monitoredIntents():
    print 'Some demands have been excluded from monitoring during TM collection: neglecting corresponding TM samples!'

# Build the TMs keeping only intentKeys related to intents currently monitored and considering the worst-case demand value
worst_TM = {intentKey: max([TM[intentKey] if intentKey in TM else 0 for TM in TMs])
            for intentKey in imrManager.monitoredIntents()}
print 'worst_TM', worst_TM

imrManager.reRouteMonitoredIntents(worst_TM)

# TODO
print 'TODO'
print "link['annotations']['bandwidth'] for host-switch links"

# TODO
print 'TODO'
print "usare Graph() o DiGraph()?!?"