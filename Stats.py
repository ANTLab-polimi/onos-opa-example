class Stats(object):
    def __init__(self, ts, bytes, packets, life, intentKey, appId, appName):
        self.ts = ts
        self.bytes = bytes
        self.packets = packets
        self.life = life
        self.intentKey = intentKey
        self.appId = appId
        self.appName = appName
