import datetime

from app import db, bcrypt
from config import Config

class User(db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, nullable=False)
    # username = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(128))
    registered_on = db.Column(db.DateTime, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False, default=0)
    balance = db.Column(db.Float, default=10000)

    def __init__(self, email, password, role_id = 0):
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password
        ).decode()
        self.registered_on = datetime.datetime.now()
        self.role_id = role_id

    def toObject(self):
        return {
            'id': self.id,
            'email': self.email,
            'balance': self.balance, 
            'role_id': self.role_id
        }
