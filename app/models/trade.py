from app import db
import datetime

class Trade(db.Model):
    __tablename__ = 'trades'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    symbol = db.Column(db.String(64), nullable=False)
    type = db.Column(db.String(64), nullable=False)
    amount = db.Column(db.Float(64), nullable = False)
    is_ftb = db.Column(db.Boolean, nullable=False)
    start_price = db.Column(db.Float, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_price = db.Column(db.Float)
    end_time = db.Column(db.DateTime)


    def __init__(self, user_id, symbol, type, amount, is_ftb, start_price, ftb_time = 0):
        self.user_id = user_id
        self.symbol = symbol
        self.type = type
        self.is_ftb = is_ftb
        self.start_price = start_price
        self.start_time = datetime.datetime.now()
        self.amount = amount
        self.ftb_time = ftb_time

    def toObject(self):
        return {
            'id': self.id,
            'symbol': self.symbol, 
            'type': self.type, 
            'startPrice': self.start_price, 
            'startTime': self.start_time, 
            'isFTB': self.is_ftb,
            'amount': self.amount, 
            'endPrice': self.end_price, 
            'endTime': self.end_time, 
        }
