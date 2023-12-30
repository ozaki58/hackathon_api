from flask import Flask, jsonify, current_app,request,Response
import json
import os
from datetime import datetime
from flask import Blueprint
import pymysql.cursors
import base64




characters_blueprint = Blueprint('characters', __name__)

#データベース設定
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
                cursor.execute('SELECT id, name, genre_id, image FROM characters WHERE genre_id = %s', (genre_id,))
            else:
                cursor.execute('SELECT id, name, genre_id, image FROM characters')
            
            # クエリの結果を取得し、Base64エンコーディングを適用
            characters_raw = cursor.fetchall()
            characters = []
            for char in characters_raw:
                char_dict = {
                    'id': char['id'],
                    'name': char['name'],
                    'genre_id': char['genre_id'],
                    'image': base64.b64encode(char['image']).decode('utf-8') if char['image'] else None
                }
                characters.append(char_dict)
        
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
                # BLOB型のimageデータがある場合、Base64にエンコード
                if 'image' in character and character['image']:
                    image_data = base64.b64encode(character['image']).decode('utf-8')
                    character['image'] = image_data
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

# キャラクターアンロック
@characters_blueprint.route('/users/<int:user_id>/characters/<int:character_id>/unlock', methods=['PATCH'])
def unlock_character(user_id, character_id):
    # データベース接続を取得
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # アンロックするキャラクターのステータスを更新するクエリを実行
            result = cursor.execute('UPDATE characters_status SET is_unlocked = %s WHERE user_id = %s AND character_id = %s', 
                                    (True, user_id, character_id))
            
            # 影響を受けた行がない場合、キャラクターが見つからないかすでにアンロックされている
            if result == 0:
                return jsonify({"error": "Character not found or already unlocked"}), 404
            
            # データベースの変更をコミット
            conn.commit()
            
            # アンロック成功のレスポンスを返す
            return jsonify({"success": "Character unlocked"}), 200
    
    except pymysql.MySQLError as e:
        # エラーハンドリング
        print(f"Error: {e}")
        conn.rollback()
        return jsonify({"error": "Database error"}), 500
    
    finally:
        conn.close()
    
#　お気に入りキャラクター設定
@characters_blueprint.route('/users/<int:user_id>/characters/<int:character_id>/favor', methods=['PATCH'])
def favor_character(user_id, character_id):
    # データベース接続を取得
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # お気に入り登録するキャラクターのステータスを更新するクエリを実行
            result = cursor.execute('UPDATE characters_status SET is_favored = %s WHERE user_id = %s AND character_id = %s', 
                                    (True, user_id, character_id))
            
            # 影響を受けた行がない場合、キャラクターが見つからないかすでにお気に入り登録されている
            if result == 0:
                return jsonify({"error": "Character not found or already favored"}), 404
            
            # データベースの変更をコミット
            conn.commit()
            
            # アンロック成功のレスポンスを返す
            return jsonify({"success": "Character favored"}), 200
    
    except pymysql.MySQLError as e:
        # エラーハンドリング
        print(f"Error: {e}")
        conn.rollback()
        return jsonify({"error": "Database error"}), 500
    
    finally:
        conn.close()

#　お気に入りキャラクター解除設定
@characters_blueprint.route('/users/<int:user_id>/characters/<int:character_id>/unfavor', methods=['PATCH'])
def unfavor_character(user_id, character_id):
    # データベース接続を取得
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # お気に入り登録するキャラクターのステータスを更新するクエリを実行
            result = cursor.execute('UPDATE characters_status SET is_favored = %s WHERE user_id = %s AND character_id = %s', 
                                    (False, user_id, character_id))
            
            # 影響を受けた行がない場合、キャラクターが見つからないかすでにお気に入り解除されている
            if result == 0:
                return jsonify({"error": "Character not found or already unfavored"}), 404
            
            # データベースの変更をコミット
            conn.commit()
            
            # アンロック成功のレスポンスを返す
            return jsonify({"success": "Character unfavored"}), 200
    
    except pymysql.MySQLError as e:
        # エラーハンドリング
        print(f"Error: {e}")
        conn.rollback()
        return jsonify({"error": "Database error"}), 500
    
    finally:
        conn.close()
    
# お気に入りキャラクター取得
@characters_blueprint.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_favorites(user_id):
    # データベース接続を取得
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # ユーザーのお気に入りキャラクターをフィルタリングするクエリを実行
            cursor.execute('SELECT * FROM characters_status WHERE user_id = %s AND is_favored = %s', (user_id, True))
            favorites = cursor.fetchall()

            # お気に入りキャラクターの詳細情報を取得する（必要に応じて）
            favorite_characters = []
            for favorite in favorites:
                cursor.execute('SELECT * FROM characters WHERE id = %s', (favorite['character_id'],))
                character = cursor.fetchone()
                if character:
                    favorite_characters.append(character)
            
            favorite_characters_encode = []
            for char in favorite_characters:
                char_dict = {
                    'id': char['id'],
                    'name': char['name'],
                    'genre_id': char['genre_id'],
                    'image': base64.b64encode(char['image']).decode('utf-8') if char['image'] else None
                }
                favorite_characters_encode.append(char_dict)

            # 結果をJSON形式でクライアントに返却
            return jsonify(favorite_characters_encode)
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()

