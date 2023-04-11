from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User
from app.models import Setting
from app.models import Trade
from app import db, marketManager
import datetime
from . import trade

@trade.route('/list', methods=['GET'])
@jwt_required()
def getCurrentTradeList():
    email = get_jwt_identity()
    try:
        user = User.query.filter_by(email = email).first()
        
        if user:
            currentTrades = Trade.query.filter_by(user_id=user.id, end_price=None).all()
            completedTrades = Trade.query.filter_by(user_id=user.id).filter(Trade.end_price != None).order_by(Trade.end_time.desc()).limit(10).all()
            responseObject = {
                'status': 'success', 
                'currentTrade': list(map(lambda trade: trade.toObject(), currentTrades)), 
                'completedTrade': list(map(lambda trade: trade.toObject(), completedTrades))
            }
            return jsonify(responseObject), 200
        else:
            responseObject = {
                'status': 'fail',
                'message': 'User does not exist'
            }
            return jsonify(responseObject), 404
    except Exception as e:
        print(e)
        responseObject = {
            'status': 'fail', 
            'message': 'Try again'
        }
        return jsonify(responseObject), 500






@trade.route('/setting', methods=['GET'])
@jwt_required()
def getTradeSettings():
    email = get_jwt_identity()
    try:
        user = User.query.filter_by(email = email).first()
        if user:
            settings = Setting.query.filter_by(user_id=user.id).first()
            
            if settings is None:
                settings = Setting(user.id)
                db.session.add(settings)
                db.session.commit()
            responseObject = {
                'status': 'success', 
                'settings': settings.toObject()
            }
            return jsonify(responseObject), 200
        else:
            responseObject = {
                'status': 'fail',
                'message': 'User does not exist'
            }
            return jsonify(responseObject), 404

    except Exception as e:
        print(e)
        responseObject = {
            'status': 'fail', 
            'message': 'Try again'
        }
        return jsonify(responseObject), 500
    
@trade.route('/setting/is-leverage', methods=['POST'])
@jwt_required()
def setIsLeverage():
    post_data = request.get_json()
    email = get_jwt_identity()
    try:
        user = User.query.filter_by(email=email).first()
        
        if user:
            setting = Setting.query.filter_by(user_id = user.id).first()
            if setting:
                setting.is_leverage = post_data.get('is_leverage')
                db.session.commit()
                responseObject = {
                    'status': 'success'
                }
                return jsonify(responseObject), 200
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return jsonify(responseObject), 401
    except Exception as e:
        print(e)
        responseObject = {
            'status': 'fail', 
            'message': 'Try Again'
        }
    
        return jsonify(responseObject), 500
    
@trade.route('/setting/leverage-value', methods=['POST'])
@jwt_required()
def setLeverageValue():
    post_data = request.get_json()
    email = get_jwt_identity()
    try:
        user = User.query.filter_by(email=email).first()
        
        if user:
            setting = Setting.query.filter_by(user_id = user.id).first()
            if setting:
                setting.leverage_value = post_data.get('leverage_value')
                db.session.commit()
                responseObject = {
                    'status': 'success'
                }
                return jsonify(responseObject), 200
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return jsonify(responseObject), 401
    except Exception as e:
        print(e)
        responseObject = {
            'status': 'fail', 
            'message': 'Try Again'
        }
    
        return jsonify(responseObject), 500
    
@trade.route('/setting/is-dynamic', methods=['POST'])
@jwt_required()
def setIsDynamic():
    post_data = request.get_json()
    email = get_jwt_identity()
    try:
        user = User.query.filter_by(email=email).first()
        
        if user:
            setting = Setting.query.filter_by(user_id = user.id).first()
            if setting:
                setting.is_dynamic = post_data.get('is_dynamic')
                db.session.commit()
                responseObject = {
                'status': 'success'
                }
                return jsonify(responseObject), 200
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return jsonify(responseObject), 401
    except Exception as e:
        print(e)
        responseObject = {
            'status': 'fail', 
            'message': 'Try Again'
        }
    
        return jsonify(responseObject), 500
    
@trade.route('/setting/static-trade', methods=['POST'])
@jwt_required()
def setStaticTrade():
    post_data = request.get_json()
    email = get_jwt_identity()
    try:
        user = User.query.filter_by(email=email).first()
        
        if user:
            setting = Setting.query.filter_by(user_id = user.id).first()
            if setting:
                setting.static_trade = post_data.get('static_trade')
                db.session.commit()
                responseObject = {
                'status': 'success'
                }
                return jsonify(responseObject), 200
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return jsonify(responseObject), 401
    except Exception as e:
        print(e)
        responseObject = {
            'status': 'fail', 
            'message': 'Try Again'
        }
    
        return jsonify(responseObject), 500
    
@trade.route('/setting/ftb', methods=['POST'])
@jwt_required()
def setFTB():
    post_data = request.get_json()
    email = get_jwt_identity()
    try:
        user = User.query.filter_by(email=email).first()
        
        if user:
            setting = Setting.query.filter_by(user_id = user.id).first()
            if setting:
                setting.ftb = post_data.get('ftb')
                db.session.commit()
                responseObject = {
                    'status': 'success'
                }
                return jsonify(responseObject), 200
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return jsonify(responseObject), 401
    except Exception as e:
        print(e)
        responseObject = {
            'status': 'fail', 
            'message': 'Try Again'
        }
    
        return jsonify(responseObject), 500

@trade.route('/start', methods=['POST'])
@jwt_required()
def startTrade():
    post_data = request.get_json()
    email = get_jwt_identity()
    try:
        user = User.query.filter_by(email=email).first()
        if user:
            setting = Setting.query.filter_by(user_id = user.id).first()
            if setting:
                if setting.is_leverage:
                    if setting.is_dynamic:
                        amount = user.balance * setting.leverage_value
                    else:
                        amount = setting.static_trade * setting.leverage_value
                else:
                    amount = setting.static_trade

                symbol = post_data.get('symbol')
                start_price = marketManager.getSpot(symbol)
                is_ftb = post_data.get('is_ftb')
                ftb_time = setting.ftb if is_ftb else 0
                trade = Trade(user.id, post_data.get('symbol'), post_data.get('type'), amount, is_ftb, start_price, ftb_time)

                db.session.add(trade)
                db.session.commit()

                responseObject = {
                    'status': 'success'
                }
                return jsonify(responseObject), 200
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return jsonify(responseObject), 401
    except Exception as e:
        print(e)
        responseObject = {
            'status': 'fail', 
            'message': 'Try Again'
        }
    
        return jsonify(responseObject), 500

    
@trade.route('/close', methods=['POST'])
@jwt_required()
def closeTrade():
    email = get_jwt_identity()
    post_data = request.get_json()
    try:
        user = User.query.filter_by(email=email).first()
        if user:
            print(post_data)
            trade = Trade.query.filter_by(id=post_data.get('tradeId')).first()
            if trade and trade.user_id == user.id:
                end_price = marketManager.getSpot(trade.symbol)
                trade.end_price = end_price
                trade.end_time = datetime.datetime.now()
                if trade.type == 'buy':
                    profit = (trade.end_price - trade.start_price) * trade.amount / trade.start_price
                else:
                    profit = (trade.start_price - trade.end_price) * trade.amount / trade.start_price
                user.balance = user.balance + profit
                db.session.commit()
                responseObject = {
                    'status': 'success'
                }
                return jsonify(responseObject), 200
            else:
                responseObject = {
                    'status': 'fail',
                    'message': 'Provide a valid trade id.'
                }
                return jsonify(responseObject), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return jsonify(responseObject), 401
    except Exception as e:
        print(e)
        responseObject = {
            'status': 'fail', 
            'message': 'Try Again'
        }
    
        return jsonify(responseObject), 500
