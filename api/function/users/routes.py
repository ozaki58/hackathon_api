from flask import Flask, jsonify, current_app,request,Response
import json
import os
from datetime import datetime
from flask import Blueprint, jsonify
import pymysql.cursors
import base64
#データベース設定
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
    
    # データベース接続を取得
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 更新するフィールドの値を取得
            name = user_data.get('name')
            email = user_data.get('email')
            
            # ユーザー情報を更新するクエリを実行
            cursor.execute(
                'UPDATE users SET name = %s, email = %s WHERE id = %s',
                (name, email, user_id)
            )
            
            # 変更があったか確認し、なければエラーを返す
            if cursor.rowcount == 0:
                return jsonify({"error": "User not found or data is the same"}), 404
            
            # データベースの変更をコミット
            conn.commit()
            
            # 更新されたユーザー情報を返す
            return jsonify({
                "id": user_id,
                "name": name,
                "email": email
            }), 200
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        conn.rollback()
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()
    