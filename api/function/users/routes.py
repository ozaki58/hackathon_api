from flask import Flask, jsonify, current_app,request,Response
import json
import os
from datetime import datetime
from flask import Blueprint, jsonify


users_blueprint = Blueprint('users', __name__)

# ユーザーIDに紐づいたユーザー情報取得
@users_blueprint.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    file_path = os.path.join(current_app.root_path, 'data', 'users.json')
    
    with open(file_path, 'r', encoding="utf-8") as f:
        users_data = json.load(f)
    
    # user_idに基づいてusersをフィルタリングする
    filtered_user = [user for user in users_data["users"] if user["id"] == user_id]
    
    user_json = json.dumps(filtered_user, ensure_ascii=False,indent=2)
    
    return Response(user_json, content_type='application/json; charset=utf-8')


#ユーザー情報を更新
@users_blueprint.route('/users/<int:user_id>', methods=['PATCH'])
def update_user(user_id):

    user_data = request.json
    if not user_data:
        return jsonify({"error": "No data provided"}), 400

    # 簡易的な実装：与えられたデータを返すだけ
    updated_user = {
        "id": user_id,
        "name": user_data.get('name', 'No name provided'),
        "email": user_data.get('email', 'No email provided')
    }
    

    user_json = json.dumps(updated_user, ensure_ascii=False,indent=2)
    
    return Response(user_json, content_type='application/json; charset=utf-8')
 
    
# ユーザー情報を更新
@users_blueprint.route('/users/<int:user_id>/coin', methods=['GET'])
def get_coin(user_id):
    file_path = os.path.join(current_app.root_path, 'data', 'coins.json')
    
    with open(file_path, 'r', encoding="utf-8") as f:
        users_data = json.load(f)
    
    # user_idに基づいてusersをフィルタリングする
    filtered_user = [coin for coin in users_data["coins"] if coin["user_id"] == user_id]
    
    user_json = json.dumps(filtered_user, ensure_ascii=False,indent=2)
    
    return Response(user_json, content_type='application/json; charset=utf-8')
