from IMRManager import IMRManager
from TopoManager import TopoManager
from utils import intent_stats

topo = TopoManager()
for stat in intent_stats():
    print stat
topo.draw_topo()

imrManager = IMRManager(topo)
imrManager.reRouteMonitoredIntents()
