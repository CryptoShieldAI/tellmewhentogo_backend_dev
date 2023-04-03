from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db, bcrypt
from app.models import User

from . import auth

@auth.route('/register', methods=['POST'])
def register():
    post_data = request.get_json()
    user = User.query.filter_by(email = post_data.get('email')).first()
    if not user:
        try:
            user = User(
                email = post_data.get('email'),
                password = post_data.get('password')
            )

            db.session.add(user)
            db.session.commit()

            auth_token = create_access_token(identity=post_data.get('email'))
            print(auth_token)
            responseObject = {
                'status': 'success',
                'message': 'Successfully registered.',
                'auth_token': auth_token,
                'user': user.toObject()
            }
            return jsonify(responseObject), 201
        except Exception as e:
            responseObject = {
                'status': 'fail', 
                'message': 'Some error occured, Please try again'
            }
        return jsonify(responseObject), 401
    else: 
        responseObject = {
            'status': 'fail',
            'message': 'User already exists, Please Log in.'
        }
        return jsonify(responseObject), 202
    



@auth.route('/login', methods=['POST'])
def login():
    post_data = request.get_json()
    try:
        user = User.query.filter_by(email = post_data.get('email')).first()
        if user and bcrypt.check_password_hash(
            user.password, post_data.get('password')
        ):
            auth_token = create_access_token(identity=post_data.get('email'))
            if auth_token:
                responseObject = {
                    'status': 'success',
                    'message': 'Successfully logged in.',
                    'auth_token': auth_token,
                    'user': user.toObject()
                }
                return jsonify(responseObject), 200
        else:
            responseObject = {
                'status': 'fail',
                'message': 'User does not exist'
            }
            return jsonify(responseObject), 404
    except Exception as e:
        responseObject = {
            'status': 'fail', 
            'message': 'Try again'
        }
        return jsonify(responseObject), 500
    
@auth.route('/user', methods=['GET'])
@jwt_required()
def getUser():
    email = get_jwt_identity()
    try:
        user = User.query.filter_by(email=email).first()
        if user: 
            responseObject = {
                'status': 'success', 
                'user': user.toObject()
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

@auth.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    responseObject = {
                'status': 'success', 
                'message': 'Successfully logged out.'
            }
    return jsonify(responseObject), 200