import re
from models import User, Manager

def update_mobile_number(number):
    number = number.strip()
    length = len(number)
    if length!=10:
        if length==11:
            if number[0]=='0': number = number[1:]
        elif length==13:
            if number.startswith('+91'): number = number[3:]
    return number

def validate_mobile_number(number):
    return bool(re.match(r'^\d{10}$', str(number)))

def validate_pan_number(pan):
    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]$'
    return bool(re.match(pattern, pan))

def validate_manager(manager_id):
    manager = Manager.query.filter_by(manager_id=manager_id).first()
    return False if (not manager or manager.is_active==False) else True

def list_users(user_list):
    list_of_user_objects = []
    for user in user_list:
        list_of_user_objects.append({
            "user_id": user.user_id,
            "manager_id": user.manager_id,
            "full_name": user.full_name,
            "mob_num": user.mob_num,
            "pan_num": user.pan_num,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "is_active": user.is_active
        })
    return list_of_user_objects