from app import db

class Setting(db.Model):
    __tablename__='settings'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_leverage = db.Column(db.Boolean, default = True)
    leverage_value = db.Column(db.Integer, default=3)
    is_dynamic = db.Column(db.Boolean, default=True)
    static_trade = db.Column(db.Float, default=10000)
    ftb = db.Column(db.Integer, default=10)

    def __init__(self, user_id):
        self.user_id = user_id

    def toObject(self):
        return {
            'is_leverage': self.is_leverage,
            'leverage_value': self.leverage_value,
            'is_dynamic': self.is_dynamic, 
            'static_trade': self.static_trade,
            'ftb': self.ftb
        }