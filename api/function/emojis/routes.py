from flask import Flask, jsonify, current_app,request,Response
import json
import os
from datetime import datetime
from flask import Blueprint
import pymysql.cursors
import base64

emojis_blueprint = Blueprint('emojis', __name__)
# #データベース設定
# def get_db_connection():
#     return pymysql.connect(host='tutorial.clmkyaosgimn.ap-northeast-1.rds.amazonaws.com',
#                     user='',
#                     db='hackathon_project',
#                     charset='utf8mb4',
#                     password='',
#                     cursorclass=pymysql.cursors.DictCursor)

def get_db_connection():
    return pymysql.connect(host='localhost',
                    user='root',
                    db='hackathon_project',
                    charset='utf8mb4',
                    password=',
                    cursorclass=pymysql.cursors.DictCursor)

#絵文字のリストを取得
@emojis_blueprint.route('/emojis', methods = ['GET'], endpoint='get_emojis')
def get_emojis():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM emojis')
            emojis_result = cursor.fetchall()  # 結果を変数に保存
        return jsonify({'emojis': emojis_result})
    
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()

@emojis_blueprint.route('/emojis/<int:user_id>', methods=['GET'],endpoint='get_emojis_by_user')
def get_emojis_filtered_users(user_id): 
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # user_emojis テーブルから特定のユーザーIDに対応する絵文字を取得
            cursor.execute('''
                SELECT ue.emoji_id, e.content, ue.date
                FROM user_emojis AS ue
                INNER JOIN emojis AS e ON ue.emoji_id = e.id
                WHERE ue.user_id = %s
            ''', (user_id,))
            emojis_result = cursor.fetchall()
        
        # 結果をJSON形式でクライアントに返却
        return jsonify({'emojis': emojis_result})
    
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()

#ユーザーが記録した絵文字を保存
@emojis_blueprint.route('/users/<int:user_id>/emojis/<int:emoji_id>/record', methods=['POST'])
def record_emoji(user_id, emoji_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 現在の日付と時刻を取得
            current_datetime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

            # 新しい絵文字データを user_emojis テーブルに挿入
            cursor.execute('''
                INSERT INTO user_emojis (user_id, emoji_id, date)
                VALUES (%s, %s, %s)
            ''', (user_id, emoji_id, current_datetime))

            # データベースの変更をコミット
            conn.commit()

            # 追加されたレコードのIDを取得
            new_record_id = cursor.lastrowid

            # 新しい絵文字データを返す
            new_emoji_data = {
                "id": new_record_id,
                "user_id": user_id,
                "emoji_id": emoji_id,
                "date": current_datetime,
            }
            return jsonify(new_emoji_data), 201

    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        conn.rollback()  # エラーが発生した場合はロールバック
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()


#特定の日付に紐づく絵文字データの取得
@emojis_blueprint.route('/users/<int:user_id>/emojis/<string:date>', methods=['GET'])
def get_emoji_filtered_date(user_id, date):
    try:
        correct_date = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Incorrect date format, should be YYYY-MM-DD"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 特定の日付に紐づく絵文字データを取得するクエリを実行
            cursor.execute('''
                SELECT ue.emoji_id, e.content, ue.date
                FROM user_emojis AS ue
                INNER JOIN emojis AS e ON ue.emoji_id = e.id
                WHERE ue.user_id = %s AND DATE(ue.date) = %s
            ''', (user_id, correct_date))
            emojis = cursor.fetchall()

            # 結果をJSON形式でクライアントに返却
            return jsonify(emojis)

    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()

#特定の期間の日付に紐づく絵文字データの取得

@emojis_blueprint.route('/users/<int:user_id>/emojis', methods=['GET'])
def get_emoji_filtered_dateterm(user_id):
    try:
        # クエリパラメータから開始日と終了日を取得
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        # URLから受け取った日付が正しい形式であるか確認する
        correct_startdate = datetime.strptime(start_date, '%Y-%m-%d').date()
        correct_enddate = datetime.strptime(end_date, '%Y-%m-%d').date()

    except ValueError:
        # 日付の形式が間違っていればエラーを返す
        return jsonify({"error": "Incorrect date format, should be YYYY-MM-DD"}), 400
    
    # データベース接続を取得
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 特定の期間に紐づく絵文字データを取得するクエリを実行
            cursor.execute('''
                SELECT ue.id, ue.user_id, ue.emoji_id, ue.date, e.content
                FROM user_emojis ue
                JOIN emojis e ON ue.emoji_id = e.id
                WHERE ue.user_id = %s AND DATE(ue.date) BETWEEN %s AND %s
            ''', (user_id, correct_startdate, correct_enddate))
            emojis = cursor.fetchall()

            # 結果をJSON形式でクライアントに返却
            return jsonify(emojis)

    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()

     

#設定された絵文字の変更
@emojis_blueprint.route('/users/<int:user_id>/emojis/<date>', methods=['PUT'])
def update_emoji(user_id, date):
    new_emoji_id = request.json.get('emoji_id')
    try:
        # URLから受け取った日付が正しい形式であるか確認する
        correct_date = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        # 日付の形式が間違えればエラーを返す
        return jsonify({"error": "Incorrect date format, should be YYYY-MM-DD"}), 400

    # データベース接続を取得
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 特定の日付に紐づく絵文字データを更新するクエリを実行
            update_result = cursor.execute('''
                UPDATE user_emojis 
                SET emoji_id = %s 
                WHERE user_id = %s AND DATE(date) = %s
            ''', (new_emoji_id, user_id, correct_date))

            # データベースの変更をコミット
            conn.commit()

            # 更新が行われたか確認
            if update_result > 0:
                return jsonify({"success": "Emoji updated successfully"}), 200
            else:
                return jsonify({"error": "No emoji was updated"}), 404

    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        conn.rollback()  # エラーが発生した場合はロールバック
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()

