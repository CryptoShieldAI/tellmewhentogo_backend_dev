from app import db

class GlobalSetting(db.Model):
    __tablename__ = 'global_settings'
    setting = db.Column(db.String(64), primary_key=True)
    settingValue = db.Column(db.String(64))

    def __init__(self, setting, settingValue):
        self.setting = setting
        self.settingValue = settingValue
