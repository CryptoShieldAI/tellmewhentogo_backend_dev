from flask import request, jsonify
from . import admin
from app.models import User, Role
from app import db

@admin.route('/user', methods=['GET'])
def getUsers():
    post_data = request.args
    emailSearch = post_data.get('email') if post_data.get('email') else ''
    try:
        users = User.query.filter(User.email.like(f"%{emailSearch}%"))
        if post_data.get('role'):
            users = users.filter_by(role_id=post_data.get('role'))
        users = users.all()
        responseObject = {
            'status': 'success', 
            'users': list(map(lambda user: user.toObject(), users))
        }
        return jsonify(responseObject), 200
    except Exception as e:
         print(e)
         responseObject = {
            'status': 'fail',
            'message': 'Some error occured, Please try again'
        }
         return jsonify(responseObject), 500
         

@admin.route('/user/roles', methods=['GET'])
def getRoles():
    try: 
        roles = Role.query.filter().all()
        responseObject = {
            'status': 'success', 
            'roles': list(map(lambda role: role.toObject(), roles))
        }
        return jsonify(responseObject), 200
    except Exception as e:
        print(e)
        responseObject = {
            'status': 'fail',
            'message': 'Some error occured, Please try again'
        }
        return jsonify(responseObject), 500

@admin.route('/user/update', methods=['POST'])
def updateUser():
    post_data = request.get_json()
    print(post_data)
    try:
        user = User.query.filter_by(id=post_data.get('id')).first()
        if user:
            user.role_id = post_data.get('role')
            user.balance = post_data.get('balance')
            db.session.commit()
            responseObject = {
                'status': 'success', 
                'message': 'update user success'
            }
            return jsonify(responseObject), 200
        else:
            responseObject ={
                'status': 'fail', 
                'message': 'The user does not exist'
            }
            return jsonify(responseObject), 404
    except Exception as e:
        print(e)
        responseObject = {
            'status': 'fail',
            'message': 'Some error occured, Please try again'
        }
        return jsonify(responseObject), 500