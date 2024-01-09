from flask import Flask, jsonify, current_app,request,Response
import json
import os
from datetime import datetime
from flask import Blueprint
import pymysql.cursors
import base64
goals_blueprint = Blueprint('goals', __name__)
#データベース設定
def get_db_connection():
    return pymysql.connect(host='localhost',
                    user='root',
                    db='hackathon_project',
                    charset='utf8mb4',
                    password='ozaki',
                    cursorclass=pymysql.cursors.DictCursor)

#特定のユーザーの目標を取得
@goals_blueprint.route('/users/<int:user_id>/goals', methods=['GET'])
def get_user_goals(user_id):
    # データベース接続を取得
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 特定のユーザーに関連する目標を取得するクエリを実行
            cursor.execute('''
                SELECT g.id, g.content
                FROM goals g
                JOIN user_goals ug ON g.id = ug.goal_id
                WHERE ug.user_id = %s
            ''', (user_id,))
            goals = cursor.fetchall()

            # 結果をJSON形式でクライアントに返却
            return jsonify(goals)
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()

#　目標を登録する
@goals_blueprint.route('/users/<int:user_id>/goals', methods=['POST'])
def set_user_goal(user_id):
    content = request.json.get('content')
    if content is None:
        return jsonify({"error": "Content is required."}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 新しい目標をデータベースに挿入するクエリを実行
            cursor.execute('INSERT INTO goals (content) VALUES (%s)', (content,))
            # 挿入された目標のIDを取得
            new_goal_id = cursor.lastrowid
            conn.commit()

            # user_goal テーブルにレコードを挿入
            cursor.execute('INSERT INTO user_goals (user_id, goal_id) VALUES (%s, %s)', (user_id, new_goal_id))
            conn.commit()

            # 新しい目標とユーザーの関係を返す
            new_user_goal = {
                "id": cursor.lastrowid,
                "user_id": user_id,
                "goal_id": new_goal_id,
                "content": content
            }
            return jsonify(new_user_goal), 201
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        conn.rollback()
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()

