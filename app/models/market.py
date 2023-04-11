from app import db

class Market(db.Model):
    __tablename__='markets'
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(64), unique=True, nullable=False)

    def __init__(self, symbol):
        self.symbol = symbol
        


