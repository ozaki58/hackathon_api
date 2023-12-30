from flask import Flask, jsonify, current_app,request,Response,Blueprint
import json
import os
from flask import current_app
from datetime import datetime


chats_blueprint = Blueprint('chats', __name__)
@chats_blueprint.route('/users/<int:user_id>/characters/<int:character_id>/date/<int:year>/<int:month>/<int:day>', methods=['GET'])
def get_chats_for_date(user_id, character_id,year, month, day):
    try:
        file_path = os.path.join(current_app.root_path, 'data', 'chats.json')
        with open(file_path, 'r', encoding="utf-8") as f:
            chats_data = json.load(f)
    except IOError:
        return jsonify({"error": "File not found"}), 404

    # 日付のフォーマットを統一する
    formatted_date = f"{year}-{month:02d}-{day:02d}"

    filtered_chats = [chat for chat in chats_data["chats"] 
                    if chat['user_id'] == user_id 
                    and chat['character_id'] == character_id 
                    and datetime.strptime(chat['created_at'].split("T")[0], '%Y-%m-%d').strftime('%Y-%m-%d') == formatted_date]
    return jsonify(filtered_chats)

    # return type(formatted_date);

@chats_blueprint.route('/users/<int:user_id>/characters/<int:character_id>/chat', methods = ['POST'])
def post_chat(user_id,character_id):

    content = request.json.get('content')
    sender_type = request.json.get('sender_type')

    if content and sender_type is None:
        return jsonify({"error": "Content and sender_type is required."}), 400
    
    new_chat_id = 1 # これはダミーのID。実際はデータベースに対応させる
    
    
    created_at = datetime.utcnow().isoformat() + 'Z'  

    # 新しいchatを作成（実際のアプリではデータベースに保存する）
    new_chat = {
        "id": new_chat_id,
        "user_id":user_id,
        "character_id":character_id,
        "content": content,
        "created_at": created_at,
        "sender_type": sender_type
    }
    
    # 新しいchatを返す
    return jsonify(new_chat), 201

@chats_blueprint.route('/chats', methods = ['GET'])    
def get_chats_history():
    user_id = request.args.get('user_id', type=int)
    character_id = request.args.get('character_id', type=int)
    sort_by = request.args.get('sort_by', default='date')
    order = request.args.get('order', default='asc')
    
    file_path = os.path.join(current_app.root_path, 'data', 'chats.json')
    
    with open(file_path, 'r', encoding="utf-8") as f:
        chats_data = json.load(f)['chats']

    # ユーザーIDとキャラクターIDでフィルタリング
    filtered_chats = [
        chat for chat in chats_data
        if chat['user_id'] == user_id and chat['character_id'] == character_id
    ]

    # 日付でソート
    if sort_by == 'date':
        filtered_chats.sort(key=lambda x: datetime.strptime(x['created_at'], '%Y-%m-%dT%H:%M:%SZ'), reverse=(order != 'asc'))

    chats_json = json.dumps(filtered_chats, ensure_ascii=False,indent=2)   
    return Response(chats_json, content_type='application/json; charset=utf-8')
