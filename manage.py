import os
from app import create_app, db, bcrypt, marketManager
from app.models.role import Role
from app.models.user import User
from app.models.market import Market
from flask_script import Manager, Shell
from flask_migrate import Migrate

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User)

manager.add_command("shell", Shell(make_context=make_shell_context))

@manager.command
def runserver():
    marketManager.initialize()
    app.run()
    
@manager.command
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

@manager.command
def createDb():
    db.create_all()

@manager.command
def dbInit():
    market = Market('BTCUSDT')
    db.session.add(market)
    db.session.commit()

if __name__ == '__main__':
    manager.run()