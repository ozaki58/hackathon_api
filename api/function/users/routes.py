from flask import Flask, jsonify, current_app,request,Response
import json
import os
from datetime import datetime
from flask import Blueprint, jsonify
import pymysql.cursors
import base64
# #データベース設定
# def get_db_connection():
#     return pymysql.connect(host='tutorial.clmkyaosgimn.ap-northeast-1.rds.amazonaws.com',
#                     user='admin',
#                     db='hackathon_project',
#                     charset='utf8mb4',
#                     password='OZaKi1030',
#                     cursorclass=pymysql.cursors.DictCursor)

def get_db_connection():
    return pymysql.connect(host='localhost',
                    user='root',
                    db='hackathon_project',
                    charset='utf8mb4',
                    password='ozaki',
                    cursorclass=pymysql.cursors.DictCursor)

users_blueprint = Blueprint('users', __name__)

# ユーザーIDに紐づいたユーザー情報取得
@users_blueprint.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # user_idを使ってユーザー情報を取得するクエリを実行
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            user = cursor.fetchone()
            
            # ユーザー情報が見つからない場合はエラーを返す
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            # 結果をJSON形式でクライアントに返却
            return jsonify(user)
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()


#ユーザー情報を更新
@users_blueprint.route('/users/<int:user_id>', methods=['PATCH'])
def update_user(user_id):
    # リクエストからユーザーのデータを取得
    user_data = request.json
    if not user_data:
        return jsonify({"error": "No data provided"}), 400
    

    user_json = json.dumps(updated_user, ensure_ascii=False,indent=2)
    
    return Response(user_json, content_type='application/json; charset=utf-8')
 
    
# ユーザー情報を更新
@users_blueprint.route('/users/<int:user_id>/coin', methods=['GET'])
def get_coin(user_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # user_coins テーブルから特定のユーザーIDに対応するコイン情報を取得
            cursor.execute('''
                SELECT user_id, amount, acquired_date, expiry_date
                FROM user_coins
                WHERE user_id = %s
            ''', (user_id,))
            user_coins = cursor.fetchall()
        
        # 結果をJSON形式でクライアントに返却
        return jsonify(user_coins)
    
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()

