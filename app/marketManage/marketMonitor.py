from collections import deque
import sched
import time
import threading
from .bybitApi import BybitApi
import pandas as pd
from .utils import *
import datetime
from app.models import User, Trade
from app import db

class MarketMonitor():
    def __init__(self, symbol, marketManager):
        self.symbol = symbol
        self.prev_price = 0
        self.current_price = 0

        self.marketManager = marketManager

        self.price_changes = deque(maxlen=self.marketManager.repeating_count)
        self.transaction_history = deque(maxlen=15)

        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.bybitApi = BybitApi(self)

        self.signal_status = 'flutuation'
        self.signal_start_time = None

        self.current_pi = 0
        self.current_rank_level = self.marketManager.rank_level
        
        self.app = marketManager.app

        self.timer_status = True
        self.second_timer = threading.Thread(target=self.run_scheduler, daemon=True)
        self.second_timer.start()

        self.initialize()

        self.trades = []

    def __del__(self):
        print("market object destory")

    def preDestroy(self):
        self.bybitApi.close_socket()
        self.timer_status = False
        self.second_timer.join()
        del self.bybitApi

    def initialize(self):
        self.second_in_cycle = 0

        self.price_history = pd.DataFrame({'ts': [], 'price': []})
        self.pricesOnSecond = pd.DataFrame({'price': []})

        self.start_cycle_time = int(time.time() * 1000)

    def run_scheduler(self):
        if self.timer_status: 
            self.scheduler.enter(1, 1, self.on_second)
            self.scheduler.run()
    
    def on_ticker(self, time, price):
        self.current_price = float(price)
        self.price_history = self.price_history.append({'ts': time, 'price': price}, ignore_index=True)

    def on_second(self):
        self.second_in_cycle += 1
        self.pricesOnSecond = self.pricesOnSecond.append({'price': self.current_price}, ignore_index=True)

        
        if self.current_price > self.prev_price:
            self.price_changes.append(1)
        elif self.current_price < self.prev_price:
            self.price_changes.append(3)
        else:
            self.price_changes.append(2)

        self.checkGrowth()

        self.checkStopFTBTrades()

        if self.second_in_cycle >= self.marketManager.cycle_duration:
            self.on_end_cycle()

        self.prev_price = self.current_price
        
        if self.timer_status:
            self.scheduler.enter(1, 1, self.on_second)
    
    def checkStopFTBTrades(self):
        current_time = datetime.datetime.now()
        trades = []
        for t in self.trades:
            if t.is_ftb and datetime.datetime.timestamp(current_time) >= datetime.datetime.timestamp(t.start_time) + t.ftb_time:
                with self.app.app_context():
                    user = User.query.filter_by(id=t.user_id).first()
                    if user:
                        trade = Trade.query.filter_by(id = t.id).first()
                        trade.end_price = self.current_price
                        trade.end_time = current_time
                        if trade.type == 'buy':
                            profit = (trade.end_price - trade.start_price) * trade.amount / trade.start_price
                        else:
                            profit = (trade.start_price - trade.end_price) * trade.amount / trade.start_price
                        user.balance = user.balance + profit
                        db.session.commit()
            else:
                trades.append(t)
        
        self.trades = trades

    def checkGrowth(self):
        if self.price_changes.count(1) >= self.marketManager.repeating_count - self.marketManager.repeating_break:
            if self.signal_status != 'pump':
                self.marketManager.removeCurrentSignals(self.symbol)
                self.signal_status = 'pump'
                self.marketManager.addCurrentSignals(self.symbol)
        elif self.price_changes.count(3) >= self.marketManager.repeating_count - self.marketManager.repeating_break:
            if self.signal_status != 'dump':
                self.marketManager.removeCurrentSignals(self.symbol)
                self.signal_status = 'dump'
                self.marketManager.addCurrentSignals(self.symbol)
        else:
            self.marketManager.removeCurrentSignals(self.symbol)
    
    def on_end_cycle(self):
        # average_price = Average(self.price_history['price'])
        self.transaction_count_in_cycle = len(self.price_history)
        self.transaction_history.append(self.transaction_count_in_cycle)
        ahmtp = average(self.transaction_history)
        levelPercents = self.marketManager.level_percents.copy()
        pi = 0
        for idx, percent in enumerate(levelPercents):
            if self.transaction_count_in_cycle > (100 + percent) * ahmtp / 100:
                pi = self.marketManager.rank_level - idx
                break
        self.current_pi = pi
        self.current_rank_level = self.marketManager.rank_level

        self.initialize()

    def getMarketHistory(self, resolution, _from, to):
        return self.bybitApi.getKline(resolution, _from, to)
    
    def addTrade(self, trade):
        self.trades.append(trade)