from app import db

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(64), unique=True)

    def __init__(self, role):
        self.role = role
        
