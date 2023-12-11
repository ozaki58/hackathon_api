from flask import Flask, jsonify, current_app,request,Response
import json
import os
from datetime import datetime
from flask import Blueprint


characters_blueprint = Blueprint('characters', __name__)

#　アプリに登録されているキャラクターリスト取得

@characters_blueprint.route('/characters', methods=['GET'])
def get_characters_list():
    file_path = os.path.join(current_app.root_path, 'data', 'characters.json')
    with open(file_path, 'r', encoding="utf-8") as f:
        all_characters= json.load(f)
    characters_json = json.dumps(all_characters, ensure_ascii=False,indent=2)
    
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

#　お気に入りキャラクター取得