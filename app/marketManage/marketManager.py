from app import db
from app.models import GlobalSetting
from app.models import LevelPercent
from app.models import Market
from .marketMonitor import MarketMonitor

class MarketManager():
    def __init__(self, app=None):
        self.app = None
        self.marketMonitors = {}
        self.current_signals = []


    def initialize(self):
        self.cycle_duration = self.getGlobalSetting('cycle_duration', 60)
        self.repeating_count = self.getGlobalSetting('repeating_count', 20)
        self.repeating_break = self.getGlobalSetting('repeating_break', 5)
        self.rank_level = self.getGlobalSetting('rank_level', 5)
        self.level_percents = self.getLevelPercents()
        if len(self.level_percents) != self.rank_level:
            self.initLevelPercent()
        markets = Market.query.all()
        for market in markets:
            self.addMarket(market.symbol)

    def initApp(self, app):
        self.app = app

    def addMarket(self, symbol):
        if self.marketMonitors.get(symbol) is not None:
            print(f'market {symbol} already exists')
            return
        market = Market(symbol)
        if market is None:
            db.session.add(market)
            db.session.commit()
        
        marketMonitor = MarketMonitor(symbol, self)
        self.marketMonitors[symbol] = marketMonitor

    def removeMarket(self, symbol):
        marketMonitor = self.marketMonitors.get(symbol)
        if marketMonitor is None:
            print(f'market {symbol} does not exist')
            return

        self.marketMonitor[symbol] = None
        marketMonitor.preDestroy()
        del marketMonitor
        market = Market.query.fitler(symbol=symbol).first()
        db.session.delete(market)
        db.session.commit()

    def getLevelPercents(self):
        levelPercents = LevelPercent.query.order_by(LevelPercent.level).all()
        return list(map(lambda levelPercent: levelPercent.percent, levelPercents))

    def initLevelPercent(self):
        LevelPercent.query.delete()
        for level in range(1, self.rank_level + 1):
            levelPercent = LevelPercent(level, 5 * level)
            db.session.add(levelPercent)
        db.session.commit()
    
    

    def getGlobalSetting(self, setting, defaultValue):
        cycleDurationSetting = GlobalSetting.query.filter_by(setting=str(setting)).first()
        if cycleDurationSetting:
            return type(defaultValue)(cycleDurationSetting.settingValue)
        else:
            cycleDurationSetting = GlobalSetting(str(setting), str(defaultValue))
            print(cycleDurationSetting)
            db.session.add(cycleDurationSetting)
            db.session.commit()
            return defaultValue
        
    def setGlobalSetting(self, setting, value):
        cycleDurationSetting = GlobalSetting.query.filter_by(setting=setting).first()
        if cycleDurationSetting:
            cycleDurationSetting.settingValue = str(value)
            db.session.commit()
        else:
            cycleDurationSetting = GlobalSetting(setting, str(value))
            db.session.add(cycleDurationSetting)
            db.session.commit()

    def getSpot(self, symbol):
        if self.marketMonitors.get(symbol) is None:
            print(f'market {symbol} does not exist')
            return 0
        return self.marketMonitors[symbol].current_price
    
    def addCurrentSignals(self, symbol):
        pass

    def removeCurrentSignals(self, symbol):
        pass

    def getCurrentSignals(self):
        symbols = list(filter(lambda symbol: self.markets.get(symbol) is not None, self.current_signals))
        return list(map(lambda symbol: self.getMarketData(symbol), symbols))
    
    def getSymbolList(self):
        markets = Market.query.all()
        return ",".join(map(lambda x: x.symbol, markets))
    
    def setCycleDuration(self, duration):
        self.setGlobalSetting('cycle_duration', duration)
        self.cycle_duration = duration

    def setRepeatingCount(self, repeating_count):
        self.setGlobalSetting('repeating_count', repeating_count)
        self.repeating_count = repeating_count

    def setRepeatingBreak(self, repeating_break):
        self.setGlobalSetting('repeating_break', repeating_break)
        self.repeating_break = repeating_break

    def setRankLevel(self, rank_level):
        self.setGlobalSetting('rank_level', rank_level)
        self.rank_level = rank_level
        self.initLevelPercent()
        self.level_percents = self.getLevelPercents()

    def setLevelPercent(self, level, percent):
        levelPercent = LevelPercent.query.filter_by(level=level).first()
        levelPercent.percent = percent
        db.session.update(levelPercent)
        db.session.commit()

    def setSymbolList(self, symbolList):
        symbols = symbolList.split(',')
        symbols = list(map(lambda x: x.strip(), symbols))
        currentSymbols = list(self.marketMonitors.keys())
        
        for symbol in currentSymbols:
            if symbol not in symbols:
                self.removeMarket(symbol)

        for symbol in symbols:
            if symbol not in currentSymbols:
                self.addMarket(symbol)
    
    def getMarketHistory(self, symbol, resolution, _from, to):
        marketMonitor = self.marketMonitors.get(symbol)
        if marketMonitor is None:
            return []
        
        return marketMonitor.getMarketHistory(resolution, _from, to)