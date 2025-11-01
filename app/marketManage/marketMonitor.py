from collections import deque
import sched
import time
import threading
from .bybitApi import BybitApi\nfrom app.models import PriceTick
import pandas as pd\nfrom app import db
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
        self.hmtp_history = deque(maxlen=15) # Pour AHMTP (15 cycles)

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

    def initialize(self):\n        self.price_ticks_buffer = []
        self.hmtp_buffer = 0
        self.second_in_cycle = 0

        # self.price_history is now obsolete, data is in DB
        self.pricesOnSecond = []

        self.start_cycle_time = int(time.time() * 1000)

    def run_scheduler(self):
        if self.timer_status: 
            self.scheduler.enter(1, 1, self.on_second)
            self.scheduler.run()
    
    def on_trade(self, ts, price):
         self.current_price = float(price)
        self.price_ticks_buffer.append(PriceTick(self.symbol, datetime.datetime.fromtimestamp(ts / 1000), self.current_price))
        self.hmtp_buffer += 1


    def on_second(self):\n        self.flush_price_ticks()
        self.second_in_cycle += 1
        self.pricesOnSecond.append(self.current_price)

        
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
        # Logique de l'algorithme original (Condition Level 1 & 2)
        
        # 1. Condition Level 1 (GR/DC) - Utilise price_changes (équivalent à CSMA)
        repeating_count = self.marketManager.repeating_count
        repeating_break = self.marketManager.repeating_break
        
        growth_count = self.price_changes.count(1)
        decline_count = self.price_changes.count(3)
        
        is_growth = growth_count >= repeating_count - repeating_break
        is_decline = decline_count >= repeating_count - repeating_break
        
        # 2. Condition Level 2 (PT20) - Simplifié pour l'instant à la persistance
        # La logique PT20 est complexe et nécessite une analyse de l'historique de prix
        # Pour l'instant, nous utilisons la détection simple comme base de GR/DC
        
        new_signal_status = 'flutuation'
        if is_growth:
            new_signal_status = 'pump'
        elif is_decline:
            new_signal_status = 'dump'
            
        # 3. Mise à jour du signal et intégration de l'Indice Volumique (VI)
        if new_signal_status != self.signal_status:
            if new_signal_status == 'flutuation':
                # Fin du signal
                self.marketManager.removeCurrentSignals(self.symbol)
                self.signal_status = new_signal_status
            else:
                # Nouveau signal (Pump ou Dump)
                # L'Indice Volumique (self.current_pi) est calculé dans on_end_cycle
                self.marketManager.removeCurrentSignals(self.symbol) # Supprime l'ancien
                self.signal_status = new_signal_status
                self.marketManager.addCurrentSignals(self.symbol) # Ajoute le nouveau avec le VI calculé
        
        # Note: La logique PT20 (répétition 20 fois avec 5 cassures) sera implémentée dans une phase ultérieure
        # car elle nécessite une refonte plus profonde de la gestion de l'état.
        # Pour l'instant, nous avons le VI (Indice de Confiance) et la détection de base.
    
    def flush_price_ticks(self):
        if self.price_ticks_buffer:
            with self.app.app_context():
                db.session.add_all(self.price_ticks_buffer)
                db.session.commit()
            self.price_ticks_buffer = []
        self.hmtp_buffer = 0

    def on_end_cycle(self):
        # 1. Calcul et stockage de l'HMTP (Indice Volumique)
        current_hmtp = self.hmtp_buffer
        self.hmtp_history.append(current_hmtp)
        self.hmtp_buffer = 0 # Réinitialise le buffer pour le nouveau cycle
        ahmtp = average(self.hmtp_history) # Calcule l'AHMTP (Average HMTP)

        # 2. Calcul de l'Indice Volumique (VI)
        volumique_index = 0
        if ahmtp > 0:
            growth_rate = (current_hmtp - ahmtp) / ahmtp * 100
            if growth_rate > 25:
                volumique_index = 5
            elif growth_rate > 20:
                volumique_index = 4
            elif growth_rate > 15:
                volumique_index = 3
            elif growth_rate > 10:
                volumique_index = 2
            elif growth_rate > 5:
                volumique_index = 1
        self.current_pi = volumique_index # Remplacer l'ancien 'pi' par le nouvel Indice Volumique

        # average_price = Average(self.pricesOnSecond)
        # self.transaction_count_in_cycle = len(self.pricesOnSecond) # Logique obsolète
        # self.transaction_history.append(self.transaction_count_in_cycle) # Logique obsolète
        # ahmtp = average(self.transaction_history) # Logique obsolète
        levelPercents = self.marketManager.level_percents.copy()
        # pi = 0 # Logique obsolète
        # for idx, percent in enumerate(levelPercents): # Logique obsolète
            # if self.transaction_count_in_cycle > (100 + percent) * ahmtp / 100: # Logique obsolète
                # pi = self.marketManager.rank_level - idx # Logique obsolète
                # break # Logique obsolète
        # self.current_pi = pi # Logique obsolète
        self.current_rank_level = self.marketManager.rank_level

        self.initialize()

    def getMarketHistory(self, resolution, _from, to):
        return self.bybitApi.getKline(resolution, _from, to)
    
    def addTrade(self, trade):
        self.trades.append(trade)