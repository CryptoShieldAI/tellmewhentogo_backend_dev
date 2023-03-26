class User():
    def __init__(self, userName, websocket, marketManager):
        self.userName = userName
        self.websocket = websocket
        self.marketManager = marketManager
        self.currentMarket = None

    def setCurrentMarket(self, symbol):
        if self.currentMarket != None:
            self.currentMarket.removeUser(self.userName)
        market = self.marketManager.markets[symbol]
        if market != None:
            market.add_subscriber(self)
        self.currentMarket = market

    def setWebsocket(self, websocket):
        if self.websocket != None:
            pass

        self.websocket = websocket
