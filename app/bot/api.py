from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User
from app.models import Bot
from app import db, marketManager
from . import bot

@bot.route('/', methods=['GET'])
@jwt_required()
def getBotList():
    pass

@bot.route('/change', methods=['POST'])
@jwt_required()
def changeBot():
    email = get_jwt_identity()
    post_data = request.get_json()
    try:
        user = User.query.filter_by(email=email).first()
        if user: 
            bot = Bot.query.filter_by(user_id=user.id, bot_number = post_data.get('bot_number')).first()
            if bot:
                if bot.enabled:
                    responseObject = {
                        'status': 'failed',
                        'message': 'the bot is enabled'
                    }
                    return jsonify(responseObject), 500
                else:
                    bot.amount = post_data.get('amount')
                    bot.leverage = post_data.get('leverage')
                    bot.number_of_orders = post_data.get('number_of_orders')
                    bot.is_simultaneous = post_data.get('is_simultaneous')
                    bot.simultaneous_number = post_data.get('simultaneous_number')
                    bot.tp = post_data.get('tp')
                    bot.sl = post_data.get('sl')
                    bot.pump = post_data.get('pump')
                    bot.dump = post_data.get('dump')
                    bot.pi_condition = post_data.get('pi_condition')
                    db.session.commit()
                    responseObject = {
                        'status': 'success',
                    }
                    return jsonify(responseObject), 200
            else:
                bot = Bot(
                    user.id, 
                    post_data.get('bot_number'), 
                    post_data.get('amount'), 
                    post_data.get('leverage'), 
                    post_data.get('number_of_orders'), 
                    post_data.get('is_simultaneous'), 
                    post_data.get('simultaneous_number'), 
                    post_data.get('tp'),
                    post_data.get('sl'), 
                    post_data.get('pump'), 
                    post_data.get('dump'), 
                    post_data.get('pi_condition')
                )

                db.session.add(bot)
                db.session.commit()
                responseObject = {
                    'status': 'success',
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
    
