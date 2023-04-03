from app import db

class LevelPercent(db.Model):
    __tablename__ = 'level_percents'
    level = db.Column(db.Integer, primary_key=True)
    percent = db.Column(db.Integer, nullable=False)

    def __init__(self, level, percent):
        self.level = level
        self.percent = percent