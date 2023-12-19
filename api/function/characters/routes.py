from flask import Flask, jsonify, current_app,request,Response
import json
import os
from datetime import datetime
from flask import Blueprint


characters_blueprint = Blueprint('characters', __name__)

#　アプリに登録されているキャラクターリスト取得

# @characters_blueprint.route('/characters', methods=['GET'])
# def get_characters_list():
#     file_path = os.path.join(current_app.root_path, 'data', 'characters.json')
#     with open(file_path, 'r', encoding="utf-8") as f:
#         all_characters= json.load(f)
#     characters_json = json.dumps(all_characters, ensure_ascii=False,indent=2)
#     return Response(characters_json, content_type='application/json; charset=utf-8')

@characters_blueprint.route('/characters', methods=['GET'])
def get_characters_list():
    # クエリパラメータからジャンルIDを取得
    genre_id = request.args.get('genre_id')
    
    file_path = os.path.join(current_app.root_path, 'data', 'characters.json')
    with open(file_path, 'r', encoding="utf-8") as f:
        all_characters = json.load(f)
    
    # ジャンルIDが提供されている場合にはそのジャンルに属するキャラクターのみをフィルタリング
    if genre_id is not None:
        filtered_characters = [character for character in all_characters['characters'] if character.get('genre_id') == genre_id]
    
    # フィルタリングされたキャラクターリストをJSON形式でクライアントに返却
    characters_json = json.dumps({'characters': filtered_characters}, ensure_ascii=False, indent=2)
    return Response(characters_json, content_type='application/json; charset=utf-8')

# id指定したキャラクター詳細取得
@characters_blueprint.route('/characters/<int:character_id>', methods=['GET'])
def get_character_datail(character_id):
    file_path = os.path.join(current_app.root_path, 'data', 'characters.json')
    with open(file_path, 'r', encoding="utf-8") as f:
        all_characters= json.load(f)
    filtered_characters = [character for character in all_characters['characters'] if character['id'] == character_id]
    
    filtered_characters_json = json.dumps(filtered_characters, ensure_ascii=False,indent=2)
    
    return Response(filtered_characters_json, content_type='application/json; charset=utf-8')


# キャラクターアンロック
@characters_blueprint.route('/users/<int:user_id>/characters/<int:character_id>/unlock', methods=['PATCH'])
def unlock(user_id,character_id):
    file_path = os.path.join(current_app.root_path, 'data', 'characters_status.json')
    with open(file_path, 'r', encoding="utf-8") as f:
        users_characters= json.load(f)
    filtered_users_characters = [users_characters for users_characters in users_characters['characters_status'] if users_characters['user_id'] == user_id and users_characters['character_id'] == character_id]
    if filtered_users_characters:
        filtered_users_characters[0]['is_unlocked'] = "True"
    else: 
        return("指定されたキャラクターIDとユーザーIDを持つようなデータはない")


    filtered_json = json.dumps(filtered_users_characters, ensure_ascii=False,indent=2)
    
    return Response(filtered_json, content_type='application/json; charset=utf-8')
    
#　お気に入りキャラクター設定
@characters_blueprint.route('/users/<int:user_id>/characters/<int:character_id>/favor', methods=['PATCH'])
def favor(user_id,character_id):
    file_path = os.path.join(current_app.root_path, 'data', 'characters_status.json')
    with open(file_path, 'r', encoding="utf-8") as f:
        users_characters= json.load(f)
    filtered_users_characters = [users_characters for users_characters in users_characters['characters_status'] if users_characters['user_id'] == user_id and users_characters['character_id'] == character_id]
    if filtered_users_characters:
        filtered_users_characters[0]['is_favored'] = "True"
    else: 
        return("指定されたキャラクターIDとユーザーIDを持つようなデータはない")


    filtered_json = json.dumps(filtered_users_characters, ensure_ascii=False,indent=2)
    
    return Response(filtered_json, content_type='application/json; charset=utf-8')
    



