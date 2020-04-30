class BestBookLevel:

    def __init__(self, nanosEpoch, time, msuk, source,
                 cbidPx, cbidSz, caskPx, caskSz,
                 bidPx, bidSz, askPx, askSz,
                 tradePx, tradeSz, seqNum, msgIdx):

        self.nanosEpoch = nanosEpoch
        self.time = time
        self.msuk = msuk
        self.source = source

        self.cbidPx = cbidPx
        self.cbidSz = cbidSz
        self.caskPx = caskPx
        self.caskSz = caskSz

        self.bidPx = bidPx
        self.bidSz = bidSz
        self.askPx = askPx
        self.askSz = askSz

        self.tradePx = tradePx
        self.tradeSz = tradeSz

        self.seqNum = seqNum
        self.msgIdx = msgIdx
