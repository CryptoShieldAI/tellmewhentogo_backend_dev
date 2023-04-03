from app import db

class Market(db.Model):
    __tablename__='markets'
    symbol = db.Column(db.String(64), primary_key=True)

    def __init__(self, symbol, marketManager=None):
        self.symbol = symbol
        


