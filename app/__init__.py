from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
from datetime import timedelta

db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()
socketio = SocketIO(cors_allowed_origins='*')

from .marketManage import MarketManager
marketManager = MarketManager()

from .models import *


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=3600)

    CORS(app)

    jwt.init_app(app)
    bcrypt.init_app(app)
    
    db.init_app(app)
    
    marketManager.initApp(app)
    
    socketio.init_app(app)    
    

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .settings import settings as settings_blueprint
    app.register_blueprint(settings_blueprint, url_prefix='/setting')

    from .trade import trade as trade_blueprint
    app.register_blueprint(trade_blueprint, url_prefix='/trade')

    return app