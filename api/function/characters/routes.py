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

# ユーザーとキャラのステータス取得
@characters_blueprint.route('/users/<int:user_id>/characters/<int:character_id>/unlock', methods=['GET'])
def get_character_user_status(user_id,character_id):
    file_path = os.path.join(current_app.root_path, 'data', 'characters_status.json')
    with open(file_path, 'r', encoding="utf-8") as f:
        all_status= json.load(f)
    filtered_characters = [status for status in all_status['characters_status'] if status['user_id'] == user_id and status['character_id'] == character_id]
    filtered_characters_json = json.dumps(filtered_characters, ensure_ascii=False,indent=2)
    
    return Response(filtered_characters_json, content_type='application/json; charset=utf-8')


# キャラクタ
@characters_blueprint.route('/users/<int:user_id>/characters/<int:character_id>/unlock', methods=['PATCH'])
def unlock(user_id, character_id):
    file_path = os.path.join(current_app.root_path, 'data', 'characters_status.json')

    with open(file_path, 'r', encoding="utf-8") as f:
        users_characters = json.load(f)

    # ユーザーとキャラクターIDに対応するエントリが既に存在するか確認
    existing_character_status = next((item for item in users_characters['characters_status'] if item['user_id'] == user_id and item['character_id'] == character_id), None)

    if existing_character_status:
        return jsonify({"error": "キャラクターは既に解放されています"}), 400

    # 新しいキャラクターステータスを追加
    new_character_status = {
        "user_id": user_id,
        "character_id": character_id,
        "is_unlocked": "True"
    }
    users_characters['characters_status'].append(new_character_status)

    # ファイルに変更を書き戻す
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(users_characters, f, ensure_ascii=False, indent=4)

    return jsonify(new_character_status), 200


#　お気に入りキャラクター設定
@characters_blueprint.route('/users/<int:user_id>/characters/<int:character_id>/favor', methods=['PATCH'])
def favor(user_id, character_id):
    file_path = os.path.join(current_app.root_path, 'data', 'characters_status.json')

    with open(file_path, 'r', encoding="utf-8") as f:
        users_characters = json.load(f)

    character_found = False
    for character in users_characters['characters_status']:
        if character['user_id'] == user_id and character['character_id'] == character_id:
            character['is_favored'] = "True"
            character_found = True
            break

    if not character_found:
        return jsonify({"message": "指定されたキャラクターIDとユーザーIDを持つようなデータはない"}), 404

    with open(file_path, 'w', encoding="utf-8") as f:
        json.dump(users_characters, f, ensure_ascii=False, indent=2)

    return jsonify({"message": "お気に入りに追加されました"}), 200

#　お気に入りキャラクター削除
@characters_blueprint.route('/users/<int:user_id>/characters/<int:character_id>/unfavor', methods=['PATCH'])
def unfavor(user_id, character_id):
    file_path = os.path.join(current_app.root_path, 'data', 'characters_status.json')

    with open(file_path, 'r', encoding="utf-8") as f:
        users_characters = json.load(f)

    character_found = False
    for character in users_characters['characters_status']:
        if character['user_id'] == user_id and character['character_id'] == character_id:
            character['is_favored'] = "false"
            character_found = True
            break

    if not character_found:
        return jsonify({"message": "指定されたキャラクターIDとユーザーIDを持つようなデータはない"}), 404

    with open(file_path, 'w', encoding="utf-8") as f:
        json.dump(users_characters, f, ensure_ascii=False, indent=2)

    return jsonify({"message": "お気に入りから削除しました"}), 200

# お気に入りキャラクター取得
@characters_blueprint.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_favorites(user_id):
    file_path = os.path.join(current_app.root_path, 'data', 'characters_status.json')
    with open(file_path, 'r', encoding="utf-8") as f:
        characters_status = json.load(f)
    # ユーザーのお気に入りキャラクターをフィルタリング
    user_favorites = [status for status in characters_status['characters_status']
                    if status['user_id'] == user_id and status['is_favored'] == "True"]
    
    return jsonify(user_favorites)

# コインの消費処理
@characters_blueprint.route('/users/<int:user_id>/consume_coins', methods=['POST'])
def consume_coins(user_id):
    file_path = os.path.join(current_app.root_path, 'data', 'coins.json')
    consumed_coins = request.json.get('consumed_coins')

    if consumed_coins is None:
        return jsonify({"error": "consumed_coins is required"}), 400

    with open(file_path, 'r', encoding="utf-8") as f:
        coins_data = json.load(f)

    # ユーザーIDに対応するコインデータを検索
    user_coins = next((coin for coin in coins_data["coins"] if coin["user_id"] == user_id), None)

    if not user_coins:
        return jsonify({"error": "User not found"}), 404

    # コインの消費
    user_coins['amount'] -= consumed_coins
    if user_coins['amount'] < 0:
        return jsonify({"error": "Insufficient coins"}), 400

    # ファイルの更新
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(coins_data, f, ensure_ascii=False, indent=4)

    return jsonify(user_coins), 200


