from Market import Market
import time
import warnings
warnings.filterwarnings("ignore")

class MarketManager():
    def __init__(self, db):
        self.markets = {}
        self.current_signals = []
        
        self.db = db

        self.initialize()

    def initialize(self):
        self.cycle_duration = int(self.db.getSetting('cycle_duration', 60))
        self.repeating_count = int(self.db.getSetting('repeating_count', 20))
        self.repeating_break = int(self.db.getSetting('repeating_break', 5))
        self.rank_level = int(self.db.getSetting('rank_level', 5))
        self.level_percents = self.db.getAllLevelPercent()
        if len(self.level_percents) != self.rank_level:
            for level in range(1, self.rank_level + 1):
                self.db.setLevelPercent(level, 5 * level)
            self.level_percents = self.db.getAllLevelPercent()
        markets = self.db.getMarketList()
        for market in markets:
            self.addMarket(market[0])

    def setCycleDuration(self, duration):
        self.db.setSetting('cycle_duration', duration)
        self.cycle_duration = duration

    def setRepeatingCount(self, repeating_count):
        self.db.setSetting('repeating_count', repeating_count)
        self.repeating_count = repeating_count

    def setRepeatingBreak(self, repeating_break):
        self.db.setSetting('repeating_break', repeating_break)
        self.repeating_break = repeating_break

    def setRankLevel(self, rank_level):
        self.db.setSetting('rank_level', rank_level)
        self.rank_level = rank_level
        self.db.removeAllLevelPercent
        for level in range(1, rank_level + 1):
            self.db.setLevelPercent(level, 5 * level)
        self.level_percents = self.db.getAllLevelPercent()

    def setLevelPercent(self, level, percent):
        self.db.setLevelPercent(level, percent)
        self.level_percents[level-1] = percent

    def getSymbolList(self):
        markets = self.db.getMarketList()
        return ",".join(map(lambda x: x[0], markets))

    def setSymbolList(self, symbolList):
        symbols = symbolList.split(',')
        symbols = list(map(lambda x: x.strip(), symbols))
        currentSymbols = list(self.markets.keys())
        for symbol in currentSymbols:
            if symbol not in symbols:    
                self.removeMarket(symbol)
        for symbol in symbols:
            if symbol not in currentSymbols:
                self.addMarket(symbol)

    def addMarket(self, symbol):
        # print(symbol)
        if self.markets.get(symbol) is not None:
            print(f'market {symbol} already exists')
            return
        self.db.insertMarket(symbol)
        market = Market(symbol, self)
        self.markets[symbol] = market

    def removeMarket(self, symbol):
        market = self.markets.get(symbol)
        if market is None:
            print(f'market {symbol} does not exist')
            return

        self.markets[symbol] = None
        market.preDestroy()
        del market
        self.db.removeMarket(symbol)

    def getSpot(self, symbol):
        if self.markets.get(symbol) is None:
            print(f'market {symbol} does not exist')
            return 0
        return self.markets[symbol].current_price

    def on_ticker(self, symbol, time, price):
        market = self.markets.get(symbol)
        if market == None:
            print(f'market {symbol} does not exist')
            return
        
        market.on_ticker(time, price)
        
    def getMarketHistory(self, symbol, resolution, _from, to):
        market = self.markets.get(symbol)
        if market == None:
            return []
        
        return market.getMarketHistory(resolution, _from, to)
    
    def addCurrentSignals(self, symbol):
        # print(symbol)
        # print(self.current_signals)
        if symbol in self.current_signals:
            return
        market = self.markets.get(symbol)
        if market is not None:
            # print(time.time())
            market.signal_start_time = time.time() - self.repeating_count
            self.current_signals.append(symbol)
            # print(self.current_signals)

    def removeCurrentSignals(self, symbol):
        if symbol in self.current_signals:
            market = self.markets.get(symbol)
            if market != None:
                try:
                    self.db.insertPumpAndDump(market.symbol, market.signal_status, 
                                            int(market.signal_start_time * 10 ** 3),
                                            int(time.time() * 10 ** 3))
                except:
                    pass
            self.current_signals.remove(symbol)

    def getMarketData(self, symbol):
        market = self.markets.get(symbol)
        return {
            'symbol': market.symbol,
            'spot': market.current_price,
            'signal_status': market.signal_status,
            'signal_start_time': market.signal_start_time,
            'pi': market.current_pi, 
            'rank_level': market.current_rank_level
        }

    def getCurrentSignals(self):
        # return list(filter(lambda market: market['vi'] > 0, list(map(lambda symbol: self.getMarketData(symbol), self.current_signals))))
        symbols = list(filter(lambda symbol: self.markets.get(symbol) is not None, self.current_signals))
        return list(map(lambda symbol: self.getMarketData(symbol), symbols))
    

if __name__ == '__main__':
    from Database import Database
    db = Database()
    marketManager = MarketManager(db)
    # marketManager.addMarket('BTCUSDT')
    # print(marketManager.getSymbolList())
    # marketManager.setSymbolList('BTCUSDT, ETHUSDT')
    # print(marketManager.getSymbolList())
    marketManager.removeMarket('BTCUSDT')

