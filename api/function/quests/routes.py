from flask import Flask, jsonify, current_app,request,Response
import json
import os
from datetime import datetime
from flask import Blueprint, jsonify

quests_blueprint = Blueprint('quests', __name__)

#目標に紐づくクエストリストの取得

@quests_blueprint.route('/users/<int:user_id>/goals/<int:goal_id>/quests', methods=['GET'])
def get_quests_for_goal(user_id, goal_id):

    file_path = os.path.join(current_app.root_path, 'data', 'quests.json')
    
    with open(file_path, 'r', encoding="utf-8") as f:
        quests_data = json.load(f)
    
    # goal_idに基づいてクエストをフィルタリングする
    filtered_quests = [quest for quest in quests_data["quests"] if quest["goal_id"] == goal_id and quest["user_id"] == user_id]
    
    quests_json = json.dumps(filtered_quests, ensure_ascii=False,indent=2)
    
    return Response(quests_json, content_type='application/json; charset=utf-8')

#クエストの詳細を取得
@quests_blueprint.route('/quests/<int:quest_id>', methods=['GET'])
def get_quest(quest_id):
    
    file_path = os.path.join(current_app.root_path, 'data', 'quests.json')
    
    with open(file_path, 'r', encoding="utf-8") as f:
        data = json.load(f)
    
    quest = [quest for quest in data["quests"] if quest['id'] == quest_id]
    
    quest_json = json.dumps(quest[0], ensure_ascii=False,indent=2)
    
    return Response(quest_json, content_type='application/json; charset=utf-8')

#クエストの詳細編集
@quests_blueprint.route('/users/<int:user_id>/goals/<int:goal_id>/quests/<int:quest_id>', methods=['PATCH'])
def quest_edit(user_id,goal_id,quest_id):
    
    
    
    file_path = os.path.join(current_app.root_path, 'data', 'quests.json')
    with open(file_path, 'r', encoding="utf-8") as f:
        quests_data = json.load(f)
    new_title = request.json.get('title')
    new_description = request.json.get('description')
    new_status = request.json.get('status')
    new_end_date = request.json.get('end_date')

    #フィルタリング
    try:
        filtered_quest = [quest for quest in quests_data["quests"] if quest["user_id"] == user_id and quest["goal_id"] == goal_id and quest["id"] == quest_id]
    
    except:
        return jsonify({"error": "指定されたデータは存在しない"}), 400
    
    #詳細を変更
    if new_title:
        filtered_quest[0]["title"] = new_title
    if new_description:
        filtered_quest[0]["description"] = new_description
    if new_status:
        filtered_quest[0]["status"] = new_status
    if new_end_date:
        filtered_quest[0]["end_date"] = new_end_date

    updated_data = filtered_quest[0]
    data_json = json.dumps(updated_data, ensure_ascii=False,indent=2)
    
    return Response(data_json, content_type='application/json; charset=utf-8')


 #クエストの完了とコインの取得
@quests_blueprint.route('/users/<int:user_id>/goals/<int:goal_id>/quests/<int:quest_id>/complete', methods=['PATCH']) 
def quest_complete(user_id,goal_id,quest_id):

    file_quests_path = os.path.join(current_app.root_path, 'data', 'quests.json')
    file_coins_path = os.path.join(current_app.root_path, 'data', 'coins.json')
    
    with open(file_quests_path, 'r', encoding="utf-8") as f:
        quests_data = json.load(f)
    with open(file_coins_path, 'r', encoding="utf-8") as f:
        coins_data = json.load(f)

    new_status = request.json.get('status')

    #questデータをフィルタリング
    try:
        filtered_quest = [quest for quest in quests_data["quests"] if quest["user_id"] == user_id and quest["goal_id"] == goal_id and quest["id"] == quest_id]
    
    except:
        return jsonify({"error": "指定されたデータは存在しない"}), 400
    
    #coinsデータをuser_idでフィルタリング
    try:
        filtered_coin = [coin for coin in coins_data["coins"] if coin["user_id"] == user_id]
    except:
        return jsonify({"error": "そのユーザーのコインデータは存在しない"}), 400
    
    try:
        if new_status == 100:
            filtered_quest[0]["status"] = new_status
            filtered_coin[0]["amount"] += 100  # 報酬を100コインとしている
        else:
            return jsonify({"error": "クエストはまだ完了していません"}), 400

    except IndexError:
        # フィルタリングされたリストが空の場合のエラーハンドリング
        return jsonify({"error": "指定されたクエストまたはコインが見つかりません"}), 404
    
    updated_data = {
        "updated_quest":filtered_quest[0],
        "updated_coin":filtered_coin[0]
    }
    data_json = json.dumps(updated_data, ensure_ascii=False,indent=2)
        
    return Response(data_json, content_type='application/json; charset=utf-8')
