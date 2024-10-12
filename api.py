import os
from datetime import datetime
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError

from lib import *
from models import *

api = Blueprint('api', __name__)

@api.route('/create_user', methods=['POST'])
def create_user():
    data = request.get_json()
    
    full_name = data.get('full_name')
    mob_num = data.get('mob_num')
    pan_num = data.get('pan_num')
    manager_id = data.get('manager_id')
    
    if not full_name or not mob_num or not pan_num:
        return jsonify({"error": "Missing required fields i.e. Full Name, Mobile Number or PAN Number"}), 400

    mob_num = update_mobile_number(mob_num)
    
    if not validate_mobile_number(mob_num):
        return jsonify({"error": "Invalid Mobile Number"}), 400

    pan_num = pan_num.strip().upper()
    if not validate_pan_number(pan_num):
        return jsonify({"error": "Invalid Pan Number"}), 400

    if manager_id and not validate_manager(manager_id):
        return jsonify({"error":"Manager is not present or inactive"}), 400

    new_user = User(
        full_name=full_name,
        mob_num=mob_num,
        pan_num=pan_num,
        manager_id=manager_id
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User created successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create user"}), 500

@api.route('/get_users', methods=['POST'])
def get_users():
    data = request.get_json()

    user_id = data.get('user_id')
    mob_num = data.get('mob_num')
    manager_id = data.get('manager_id')

    try:
        if not user_id and not mob_num and not manager_id: 
            user = User.query.all()
            user_list = list_users(user)
            return jsonify({"users":user_list}), 200

        if user_id:
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                return jsonify({"error": "User not found with given user id"}), 404
            user_list = list_users([user])
            return jsonify({"users":user_list}), 200
        
        if mob_num:
            users = User.query.filter_by(mob_num=mob_num).all()
            if not users:
                return jsonify({"error": "User not found with given mobile number"}), 404
            user_list = list_users(users)
            return jsonify({"users":user_list}), 200

        if manager_id:
            manager = Manager.query.filter_by(manager_id=manager_id)
            if not manager:
                return jsonify({"error":"Manager not found with given manager id"}), 404

            user = User.query.filter_by(manager_id=manager_id)
            user_list = list_users(user)
            return jsonify({"users":user_list}), 200

    except SQLAlchemyError as e:
        db.session.rollback() 
        return jsonify({"error": "Database error occurred while fetching users"}), 500

    except Exception as e:
        return jsonify({"error": "Failed to fetch user"}), 500

@api.route('/delete_user', methods=['POST'])
def delete_user():
    data = request.get_json()

    user_id = data.get('user_id')
    mob_num = data.get('mob_num')

    if not user_id and not mob_num: 
        return jsonify({"error":"Please provide user_id or mob_num to delete specific user"}), 400

    try:

        if user_id:
            if User.query.filter_by(user_id=user_id).count()>0:
                User.query.filter_by(user_id=user_id).delete()
                db.session.commit()
                return jsonify({"message":"User deleted successfully"}), 200
            else:
                return jsonify({"error": "User not found with given user id"}), 404

        if mob_num:
            if User.query.filter_by(mob_num=mob_num).count()>0:
                User.query.filter_by(mob_num=mob_num).delete()
                db.session.commit()
                return jsonify({"message":"User deleted successfully"}), 200
            else:
                return jsonify({"error": "User not found with given mobile number"}), 404
            
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error occurred while deleting users"}), 500

    except Exception as e:
        return jsonify({"error": "Failed to delete user"}), 500

@api.route('/update_user', methods=['POST'])
def update_user():
    data = request.json
    user_ids = data.get('user_ids')
    update_data = data.get('update_data') 

    manager_id = update_data.get('manager_id')
    mob_num = update_data.get('mob_num', None)
    pan_num = update_data.get('pan_num', None)
    full_name = update_data.get('full_name', None)

    if not manager_id:
        return jsonify({"message":"Manager Id is required."}), 400

    if not validate_manager(manager_id):
        return jsonify({"message":"Manager with given id is not present"}), 404

    if full_name!=None:
        if not full_name:
            return jsonify({"message":"Full name can not be empty"}), 400

    if mob_num!=None:
        mob_num = update_mobile_number(mob_num)
        if not validate_mobile_number(mob_num):
            return jsonify({"message": "Invalid Mobile Number"}), 400

    if pan_num!=None:
        pan_num = pan_num.strip().upper()
        if not validate_pan_number(pan_num):
            return jsonify({"message": "Invalid Pan Number"}), 400

    try:
        users = User.query.filter(User.user_id.in_(user_ids)).all()
        
        existing_user_ids = {user.user_id for user in users}

        for user_id in user_ids:
            if user_id not in existing_user_ids:
                return jsonify({'error': 'Some user with provided id are not found'}), 404

        matching_manager_ids = [user.manager_id for user in users if user.manager_id == manager_id]

        if matching_manager_ids:
            return jsonify({'error': 'These keys can be updated on a individual basis only and not in bulk'}), 400

        for user in users:
            if user.manager_id==None:
                user.full_name = full_name if full_name else user.full_name
                user.mob_num = mob_num if mob_num else user.mob_num
                user.pan_num = pan_num if pan_num else user.pan_num
                user.manager_id = manager_id
                user.update()
            else:
                user.is_active = False
                new_user = User(
                    full_name = full_name if full_name else user.full_name,
                    mob_num = mob_num if mob_num else user.mob_num,
                    pan_num = pan_num if pan_num else user.pan_num,
                    manager_id = manager_id,
                    created_at = datetime.utcnow(),
                    updated_at = datetime.utcnow()
                )
                db.session.add(new_user)
                db.session.commit()

        return jsonify({"message":"user updated successfully"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error occurred while updating users"}), 500

    except Exception as e:
        return jsonify({"error": "Failed to update user"}), 500

@api.route('/create_manager', methods=['POST'])
def create_manager():
    data = request.get_json()
    
    full_name = data.get('full_name')
    
    if not full_name:
        return jsonify({"error": "Missing required fields i.e. Full Name"}), 400

    manager = Manager(
        full_name=full_name
    )

    try:
        db.session.add(manager)
        db.session.commit()
        return jsonify({"message": "Manager created successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create Manager"}), 500