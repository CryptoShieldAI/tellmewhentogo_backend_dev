import sqlite3
import time

class Database():
    def __init__(self):
        self.con = sqlite3.connect("/home/hams/trading/server/bybit.db", check_same_thread=False)
        self.cur = self.con.cursor()
        self.initializeDB()

    def initializeDB(self):
        self.cur.execute("CREATE TABLE IF NOT EXISTS signals(symbol, type, start_time, end_time)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS markets(symbol type unique)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS settings(key type unique, value)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS level_percents(level type unique, percent)")

    def insertMarket(self, symbol):
        self.cur.execute(f"Insert or replace Into markets Values('{symbol}')")
        self.con.commit()

    def removeMarket(self, symbol):
        self.cur.execute(f"Delete From markets Where symbol='{symbol}'")
        self.con.commit()
    
    def getMarketList(self):
        self.cur.execute("Select symbol from markets")
        rows = self.cur.fetchall()
        return rows

    def getSetting(self, key, default):
        self.cur.execute(f"Select key, value From settings where key='{key}'")
        row = self.cur.fetchone()
        if row is None:
            return default
        else:
            return row[1]

    def setSetting(self, key, value):
        self.cur.execute(f"insert or replace into settings values('{key}', '{value}')")
        self.con.commit()

    def getLevelPercent(self, level):
        self.cur.execute(f"Select level, percent from level_percents where level={level}")
        row = self.cur.fetchone
        if row is None: 
            return 0
        return row[1]
    
    def setLevelPercent(self, level, percent):
        self.cur.execute(f"insert or replace into level_percents values({level}, {percent})")
        self.con.commit()
    
    def getAllLevelPercent(self):
        self.cur.execute(f"select level, percent from level_percents order by level")
        rows = self.cur.fetchall()
        return list(map(lambda x: x[1], rows))

    def removeAllLevelPercent(self):
        self.cur.execute(f"delete from level_percents")
        self.con.commit

    def insertSignals(self, symbol, type, start_time, end_time):
        self.cur.execute("Insert Into signals Values(?, ?, ?, ?)", 
                         (symbol, type, start_time, end_time))

        self.con.commit()

    def getPumpList(self, period):
        currentTime = time.time()
        startTime = currentTime - (24 * 3600 if period == 'day' else 24 * 3600 * 7)
        startTime = int(startTime * 1000)
        sql = f"Select markets.symbol, T.count \
            From markets \
            Left Join (Select symbol, count(*) as count \
            From signals \
            Where type='pump' and start_time > ?\
            Group by symbol) T \
            On markets.symbol=T.symbol \
            Order by T.count Desc \
            Limit 10"
        self.cur.execute(sql, (startTime,))
        rows = self.cur.fetchall()
        return rows


    def getDumpList(self, period):
        currentTime = time.time()
        startTime = currentTime - (24 * 3600 if period == 'day' else 24 * 3600 * 7)
        startTime = int(startTime * 1000)
        sql = f"Select markets.symbol, T.count \
            From markets \
            Left Join (Select symbol, count(*) as count \
            From signals \
            Where type='dump' and start_time > ?\
            Group by symbol) T \
            On markets.symbol=T.symbol \
            Order by T.count Desc\
            Limit 10"
        self.cur.execute(sql, (startTime,))
        rows = self.cur.fetchall()
        return rows

if __name__ == '__main__':
    db = Database()
    db.setLevelPercent(0, 5)
    db.setLevelPercent(1, 10)
    print(db.getAllLevelPercent())
