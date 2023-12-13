from flask import Flask, jsonify, current_app,request,Response
import json
import os
from datetime import datetime
from flask import Blueprint


emojis_blueprint = Blueprint('emojis', __name__)

#絵文字のリストを取得
@emojis_blueprint.route('/emojis', methods = ['GET'])
def get_emojis():
    file_path = os.path.join(current_app.root_path, 'data', 'emojis.json')
    
    with open(file_path, 'r', encoding="utf-8") as f:
        emojis_data = json.load(f)
    
    # user_idに基づいてusersをフィルタリングする
    
    
    emojis_json = json.dumps(emojis_data, ensure_ascii=False,indent=2)
    
    return Response(emojis_json, content_type='application/json; charset=utf-8')



#ユーザーが記録した絵文字を保存
@emojis_blueprint.route('/users/<int:user_id>/emojis/<int:emoji_id>/record', methods=['POST'])
def record_emoji(user_id,emoji_id):

    id = 1 # これはダミーのID。実際はデータベースに対応させる
    
  
    recorded_at = datetime.utcnow().isoformat() + 'Z'  

    # emojiを記録（実際のアプリではデータベースに保存する）
    recorded_emoji = {
        "id": id,
        "user_id": user_id,
        "emoji_id": emoji_id,
        "date": recorded_at
    }
    
    # 新しい目標を返す
    return jsonify(recorded_emoji), 201


#特定の日付に紐づく絵文字データの取得
@emojis_blueprint.route('/users/<int:user_id>/emojis/<date>', methods=['GET'])
def get_emoji_filtered_date(user_id, date):
    # dateの形式を確認する
    try:
        # URLから受け取った日付が正しい形式であるか確認する
        correct_date = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        # 日付の形式が間遍えればエラーを返す
        return jsonify({"error": "Incorrect date format, should be YYYY-MM-DD"}), 400
    
    file_path = os.path.join(current_app.root_path, 'data', 'user_emojis.json')
    with open(file_path, 'r', encoding="utf-8") as f:
        user_emojis_data = json.load(f)
    
    # emojiのリストをuser_idと正しい形式のdateでフィルタする
    filtered_emoji = [
        emoji for emoji in user_emojis_data['user_emojis']
        if emoji['user_id'] == user_id and emoji['date'] == correct_date.isoformat()
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
