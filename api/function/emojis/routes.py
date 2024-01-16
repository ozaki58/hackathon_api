from flask import Flask, jsonify, current_app,request,Response
import json
import os
from datetime import datetime
from flask import Blueprint


emojis_blueprint = Blueprint('emojis', __name__)

#絵文字のリストを取得
@emojis_blueprint.route('/emojis', methods = ['GET'], endpoint='get_emojis')
def get_emojis():
    file_path = os.path.join(current_app.root_path, 'data', 'emojis.json')
    
    with open(file_path, 'r', encoding="utf-8") as f:
        emojis_data = json.load(f)
    
    # user_idに基づいてusersをフィルタリングする
    emojis_json = json.dumps(emojis_data, ensure_ascii=False,indent=2)
    
    return Response(emojis_json, content_type='application/json; charset=utf-8')

@emojis_blueprint.route('/emojis/<int:user_id>', methods=['GET'],endpoint='get_emojis_by_user')
def get_emojis_filtered_users(user_id): 
    file_path = os.path.join(current_app.root_path, 'data', 'user_emojis.json')

    with open(file_path, 'r', encoding="utf-8") as f:
        emojis_data = json.load(f)

    # user_idに基づいて絵文字データをフィルタリング
    filtered_emojis = [emoji for emoji in emojis_data['user_emojis'] if emoji['user_id'] == int(user_id)]

    # 必要なフォーマットに変換
    formatted_emojis = []
    for emoji in filtered_emojis:
        emoji_title = emoji['emoji_id']  # emoji_idに基づいて適切な絵文字タイトルを割り当てる
        formatted_emojis.append({'title': emoji_title, 'date': emoji['date']})

    return jsonify(formatted_emojis)

#ユーザーが記録した絵文字を保存
@emojis_blueprint.route('/users/<int:user_id>/emojis/<int:emoji_id>/record', methods=['POST'])
def record_emoji(user_id,emoji_id):
    # JSONファイルを読み込む
    try:
        file_path = os.path.join(current_app.root_path, 'data', 'user_emojis.json')
        with open(file_path, 'r') as file:
            data = json.load(file)
    except (IOError, json.JSONDecodeError):
        data = {'user_emojis': []}

    # 新しい絵文字データを作成
    new_emoji_data = {
        "id": len(data['user_emojis']) + 1,  # 新しいIDを生成
        "user_id": user_id,
        "emoji_id": emoji_id,
        "date": datetime.utcnow().isoformat() + 'Z',
    }

    # データを追加
    data['user_emojis'].append(new_emoji_data)

    # ファイルに書き戻す
    try:
        file_path = os.path.join(current_app.root_path, 'data', 'user_emojis.json')
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
    except IOError:
        return jsonify({"error": "Could not save data"}), 500

    # 新しい絵文字データを返す
    return jsonify(new_emoji_data), 201


#特定の日付に紐づく絵文字データの取得
@emojis_blueprint.route('/users/<int:user_id>/emojis/<date>', methods=['GET'])
def get_emoji_filtered_date(user_id, date):
    try:
        correct_date = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Incorrect date format, should be YYYY-MM-DD"}), 400

    file_path = os.path.join(current_app.root_path, 'data', 'user_emojis.json')
    with open(file_path, 'r', encoding="utf-8") as f:
        user_emojis_data = json.load(f)

    filtered_emoji = [
        emoji for emoji in user_emojis_data['user_emojis']
        if emoji['user_id'] == user_id and datetime.strptime(emoji['date'].split('T')[0], '%Y-%m-%d').date() == correct_date
    ]

    return jsonify(filtered_emoji)

#特定の期間の日付に紐づく絵文字データの取得
@emojis_blueprint.route('/users/<int:user_id>/emojis', methods=['GET'])
def get_emoji_filtered_dateterm(user_id):
    # dateの形式を確認する
    try:
        req = request.args
        start_date = req.get("start_date")
        end_date = req.get("end_date")

        # URLから受け取った日付が正しい形式であるか確認する
        correct_startdate = datetime.strptime(start_date, '%Y-%m-%d').date()
        correct_enddate = datetime.strptime(end_date, '%Y-%m-%d').date()

    except ValueError:
        # 日付の形式が間遍えればエラーを返す
        return jsonify({"error": "Incorrect date format, should be YYYY-MM-DD"}), 400
    
    file_path = os.path.join(current_app.root_path, 'data', 'user_emojis.json')
    with open(file_path, 'r', encoding="utf-8") as f:
        user_emojis_data = json.load(f)
    
     

    # emojiのリストをuser_idと指定された期間でフィルタする
    filtered_emoji = [
        emoji for emoji in user_emojis_data['user_emojis']
        if emoji['user_id'] == user_id 
        and correct_startdate <= datetime.strptime(emoji['date'], '%Y-%m-%d').date() <= correct_enddate
    ]  
    return jsonify(filtered_emoji)

#設定された絵文字の変更
@emojis_blueprint.route('/users/<int:user_id>/emojis/<date>', methods=['PUT'])
def update_emoji(user_id,date):

    file_path = os.path.join(current_app.root_path, 'data', 'user_emojis.json')
    with open(file_path, 'r', encoding="utf-8") as f:
        user_emojis_data = json.load(f)
    new_emoji_id = request.json.get('emoji_id')
    correct_date = datetime.strptime(date, '%Y-%m-%d').date()

    #フィルタリング
    try:
        filtered_recorded_emoji_id = [
            emoji for emoji in user_emojis_data['user_emojis'] if datetime.strptime(emoji['date'], '%Y-%m-%d').date()  == correct_date
            and emoji['user_id'] == user_id]
    except:
        return jsonify({"error": "指定されたデータは存在しない"}), 400
    
    #絵文字を変更
    filtered_recorded_emoji_id[0]["emoji_id"] = new_emoji_id
    
    updated_data = filtered_recorded_emoji_id
    data_json = json.dumps(updated_data, ensure_ascii=False,indent=2)
    
    return Response(data_json, content_type='application/json; charset=utf-8')
