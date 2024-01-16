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


chats_blueprint = Blueprint('chats', __name__)
@chats_blueprint.route('/users/<int:user_id>/characters/<int:character_id>/date/<int:year>/<int:month>/<int:day>', methods=['GET'])
def get_chats_for_date_character(user_id, character_id,year, month, day):
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

@chats_blueprint.route('/users/<int:user_id>/date/<int:year>/<int:month>/<int:day>', methods=['GET'])
def get_chats_for_date(user_id,year, month, day):
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
                    and datetime.strptime(chat['created_at'].split("T")[0], '%Y-%m-%d').strftime('%Y-%m-%d') == formatted_date]
    return jsonify(filtered_chats)

@chats_blueprint.route('/users/<int:user_id>/characters/<int:character_id>/chat', methods=['POST'])
def post_chat(user_id, character_id):
    content = request.json.get('content')
    

    if not content or sender_type is None:
        return jsonify({"error": "Content and sender_type are required."}), 400

    # chats.json ファイルのパスを取得
    file_path = os.path.join(current_app.root_path, 'data','chats.json')

    # chats.json ファイルを読み込む
    with open(file_path, 'r', encoding='utf-8') as file:
        chats = json.load(file)

    # 新しいチャットメッセージを作成
    new_chat = {
        "id": len(chats['chats']) + 1,  # 仮のID生成
        "user_id": user_id,
        "character_id": character_id,
        "content": content,
        "created_at": datetime.utcnow().isoformat() + 'Z',
        "sender_type": sender_type
    }

    # チャットリストに新しいメッセージを追加
    chats['chats'].append(new_chat)

    # 更新されたデータをファイルに書き戻す
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(chats, file, ensure_ascii=False, indent=4)

    return jsonify(new_chat), 201

    return jsonify(new_chat), 201
def get_completion(prompt, client_instance, user_id,character_id ,model="gpt-3.5-turbo-1106"):
  character_prompt = get_character_prompt(character_id)
  past_chats = get_past_chats(user_id, character_id)
  messages = [{"role": "system", "content": character_prompt}
              ]
  messages.extend(
        {"role": "user" if chat['sender_type'] == 0 else "assistant", "content": chat['content']}
        for chat in past_chats
  )
  messages.append({"role": "user", "content": prompt})
  response = client_instance.chat.completions.create(
  model=model,
  messages=messages,
  max_tokens=3000,
  temperature=0,
  )
  return response.choices[0].message.content

#キャラクターのプロンプトを取得する関数
def get_character_prompt(character_id):
    with conn.cursor() as cursor:
        cursor.execute(
            'SELECT prompt FROM characters WHERE id = %s', (character_id,)
        )
        result = cursor.fetchone()
        if result:
            return result['prompt']
        else:
            return None  # キャラクターが見つからない場合はNoneを返す
# チャット履歴を取得
def get_past_chats(user_id, character_id):
    with conn.cursor() as cursor:
        cursor.execute(
            'SELECT content, sender_type FROM chats WHERE user_id = %s AND character_id = %s ORDER BY created_at ASC',
            (user_id, character_id)
        )
        chats = cursor.fetchall()
        return chats
    

#チャットの履歴を取得する
@chats_blueprint.route('/chats', methods = ['GET'])    
def get_chats_history():
    user_id = request.args.get('user_id', type=int)
    character_id = request.args.get('character_id', type=int)
    sort_by = request.args.get('sort_by', default='date')
    order = request.args.get('order', default='asc')

    with conn.cursor() as cursor:
        cursor.execute(
            'SELECT * FROM chats WHERE user_id = %s AND character_id = %s ', (user_id,character_id)
        )
        result = cursor.fetchall()
        
    

    # 日付でソート
    if sort_by == 'date':
        result.sort(key=lambda x: x['created_at'], reverse=(order != 'asc'))

    chats_json = json.dumps(filtered_chats, ensure_ascii=False,indent=2)   
    return Response(chats_json, content_type='application/json; charset=utf-8')
