from app import db

class PriceTick(db.Model):
    __tablename__ = 'price_ticks'
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(64), index=True)
    timestamp = db.Column(db.DateTime, index=True)
    price = db.Column(db.Float)

    def __init__(self, symbol, timestamp, price):
        self.symbol = symbol
        self.timestamp = timestamp
        self.price = price

    def __repr__(self):
        return f'<PriceTick {self.symbol} - {self.timestamp} - {self.price}>'
