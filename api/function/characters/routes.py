from flask import Flask, jsonify, current_app,request,Response
import json
import os
from datetime import datetime
from flask import Blueprint
import pymysql.cursors
import base64




characters_blueprint = Blueprint('characters', __name__)

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

# 　アプリに登録されているキャラクターリスト取得
@characters_blueprint.route('/characters', methods=['GET'])
def get_characters_list():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # クエリパラメータからジャンルIDを取得
            genre_id = request.args.get('genre_id', type=int)
            # ジャンルIDが提供されている場合はそのジャンルに属するキャラクターのみをフィルタリング
            if genre_id is not None:
                cursor.execute('SELECT * FROM characters WHERE genre_id = %s', (genre_id,))
            else:
                cursor.execute('SELECT * FROM characters')
            
            # クエリの結果を取得
            characters = cursor.fetchall()
        
        # 結果をJSON形式でクライアントに返却
        return jsonify({'characters': characters})
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()



# id指定したキャラクター詳細取得
@characters_blueprint.route('/characters/<int:character_id>', methods=['GET'])
def get_character_detail(character_id):
    # データベース接続を取得
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 指定されたIDのキャラクターの詳細を取得するクエリを実行
            cursor.execute('SELECT * FROM characters WHERE id = %s', (character_id,))
            character = cursor.fetchone()
            if character:
                # JSONとしてレスポンスを返す
                return jsonify(character)
            else:
                # キャラクターが見つからない場合は404エラーを返す
                return jsonify({"error": "Character not found"}), 404
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()



# ユーザーとキャラのステータス取得
@characters_blueprint.route('/users/<int:user_id>/characters/<int:character_id>/unlock', methods=['GET'])
def get_character_user_status(user_id, character_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 指定されたユーザーIDとキャラクターIDに該当するステータス情報を取得
            cursor.execute('''
                SELECT * FROM characters_status 
                WHERE user_id = %s AND character_id = %s
            ''', (user_id, character_id))
            character_status = cursor.fetchone()

            if character_status:
                return jsonify(character_status)
            else:
                return jsonify({"error": "Character status not found"}), 404

    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()


# キャラクタ
@characters_blueprint.route('/users/<int:user_id>/characters/<int:character_id>/unlock', methods=['PATCH'])
def unlock(user_id, character_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # ユーザーとキャラクターIDに対応するエントリが既に存在するか確認
            cursor.execute('''
                SELECT * FROM characters_status 
                WHERE user_id = %s AND character_id = %s
            ''', (user_id, character_id))
            existing_character_status = cursor.fetchone()

            if existing_character_status:
                return jsonify({"error": "キャラクターは既に解放されています"}), 400

            # 新しいキャラクターステータスを追加
            cursor.execute('''
                INSERT INTO characters_status (user_id, character_id,is_favored, is_unlocked) 
                VALUES (%s, %s, 0,1)
            ''', (user_id, character_id))

            # データベースの変更をコミット
            conn.commit()

            # 追加されたレコードの詳細を取得
            new_character_status = {
                "user_id": user_id,
                "character_id": character_id,
                "is_unlocked": True
            }

            return jsonify(new_character_status), 200

    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        conn.rollback()  # エラーが発生した場合はロールバック
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()



#　お気に入りキャラクター設定
@characters_blueprint.route('/users/<int:user_id>/characters/<int:character_id>/favor', methods=['PATCH'])
def favor(user_id, character_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 指定されたキャラクターステータスのレコードを取得
            cursor.execute('SELECT * FROM characters_status WHERE user_id = %s AND character_id = %s', (user_id, character_id))
            character_status = cursor.fetchone()

            if not character_status:
                return jsonify({"message": "指定されたキャラクターIDとユーザーIDを持つようなデータはない"}), 404

            # お気に入りステータスを更新
            cursor.execute('UPDATE characters_status SET is_favored = 1 WHERE id = %s', (character_status['id'],))
            conn.commit()

            return jsonify({"message": "お気に入りに追加されました"}), 200

    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        conn.rollback()
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()


#　お気に入りキャラクター削除
@characters_blueprint.route('/users/<int:user_id>/characters/<int:character_id>/unfavor', methods=['PATCH'])
def unfavor(user_id, character_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 指定されたキャラクターステータスのレコードを取得
            cursor.execute('SELECT * FROM characters_status WHERE user_id = %s AND character_id = %s', (user_id, character_id))
            character_status = cursor.fetchone()

            if not character_status:
                return jsonify({"message": "指定されたキャラクターIDとユーザーIDを持つようなデータはない"}), 404

            # お気に入りステータスを更新（解除）
            cursor.execute('UPDATE characters_status SET is_favored = 0 WHERE id = %s', (character_status['id'],))
            conn.commit()

            return jsonify({"message": "お気に入りから削除しました"}), 200

    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        conn.rollback()
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()


# お気に入りキャラクター取得
@characters_blueprint.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_favorites(user_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # characters_status テーブルから特定のユーザーIDに対応するお気に入りキャラクター情報を取得
            cursor.execute('''
                SELECT id, user_id, character_id, is_favored, is_unlocked
                FROM characters_status
                WHERE user_id = %s AND is_favored = 1
            ''', (user_id,))
            user_favorites = cursor.fetchall()
        
        # 結果をJSON形式でクライアントに返却
        return jsonify(user_favorites)
    
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()

# コインの消費処理
@characters_blueprint.route('/users/<int:user_id>/consume_coins', methods=['POST'])
def consume_coins(user_id):
    consumed_coins = request.json.get('consumed_coins')

    if consumed_coins is None:
        return jsonify({"error": "consumed_coins is required"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # ユーザーIDに対応するコイン残高を検索
            cursor.execute("SELECT amount FROM user_coins WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()

            if not result:
                return jsonify({"error": "User not found"}), 404

            # 新しいコイン残高を計算
            new_amount = result['amount'] - consumed_coins
            if new_amount < 0:
                return jsonify({"error": "Insufficient coins"}), 400

            # コイン残高を更新
            cursor.execute("UPDATE user_coins SET amount = %s WHERE user_id = %s", (new_amount, user_id))
            conn.commit()

            return jsonify({"user_id": user_id, "new_amount": new_amount}), 200
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        conn.rollback()
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()

