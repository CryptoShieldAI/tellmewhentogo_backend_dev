import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from app import create_app, db, marketManager
from app.models.role import Role
from app.models.user import User
from app.models.market import Market\nfrom app.models.priceTick import PriceTick
from flask_migrate import Migrate
import warnings
import click
import unittest

warnings.filterwarnings("ignore")

# Initialize app
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


# Setup logging
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/flask_app.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Flask app startup')

@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, User=User)

@app.cli.command("initialize_market")
def initialize_market():
    """Initialize the market manager."""
    marketManager.initialize()

@app.cli.command("custom_runserver")
def custom_runserver():
    """Run the Flask development server."""
    marketManager.initialize()
    click.echo("Server is running... Use flask run instead for default behavior.")

@app.cli.command("dev")
@click.option('--port', default=5001, help='Port to run the server on.')
def dev(port):
    """Run the Flask development server on a custom port."""
    marketManager.initialize()
    os.environ['FLASK_RUN_PORT'] = str(port)
    click.echo(f"Running on port {port}...")
    os.system(f"flask run --port {port}")

@app.cli.command("test")
def test():
    """Run the unit tests."""
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

@app.cli.command("create_db")
def create_db():
    """Create the database."""
    db.create_all()

@app.cli.command("db_init")
def db_init():
    """Initialize the database with initial data."""
    market = Market('BTCUSDT')
    db.session.add(market)
    db.session.commit()

if __name__ == '__main__':
    app.run()
