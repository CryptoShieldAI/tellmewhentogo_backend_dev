from app import db

class Signal(db.Model):
    __tablename__ = 'signals'
    id = db.Column(db.Integer, primary_key = True)
    symbol = db.Column(db.String(64), index=True,  nullable=False)
    type = db.Column(db.String(64), index=True, nullable = False)
    start_time = db.Column(db.DateTime, index=True, nullable=False)
    end_time = db.Column(db.DateTime)

    def __init__(self, symbol, type, start_time, end_time=None):
        self.symbol = symbol
        self.type = type
        self.start_time = start_time
        self.end_time = end_time