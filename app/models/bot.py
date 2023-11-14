from app import db

class Bot(db.Model):
    __tablename__ = 'bots'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    bot_number = db.Column(db.Integer, nullable = False)
    amount = db.Column(db.Float(64), nullable = False)
    leverage = db.Column(db.Float(64), nullable = False)
    number_of_orders = db.Column(db.Integer, default = 10)
    is_simultaneous = db.Column(db.Boolean, default = False)
    simultaneous_number = db.Column(db.Boolean, default = 0)
    tp = db.Column(db.Float(64), default = 10)
    sl = db.Column(db.Float(64), default = 3.5)
    pump = db.Column(db.Boolean, default=True)
    dump = db.Column(db.Boolean, default=True)
    pi_condition = db.Column(db.Float(64), default=0.4)
    enabled = db.Column(db.Boolean, default=False)
    
    def __init__(self, 
                user_id, 
                bot_number, 
                amount, 
                leverage
                ):
        self.user_id = user_id
        self.bot_number = bot_number
        self.amount = amount
        self.leverage = leverage
    
    
