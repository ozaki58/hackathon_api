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

    try:
        quest_index = next(index for index, quest in enumerate(quests_data["quests"]) if quest["user_id"] == user_id and quest["goal_id"] == goal_id and quest["id"] == quest_id)
    except StopIteration:
        return jsonify({"error": "指定されたデータは存在しない"}), 400

    if new_title:
        quests_data["quests"][quest_index]["title"] = new_title
    if new_description:
        quests_data["quests"][quest_index]["description"] = new_description
    if new_status:
        quests_data["quests"][quest_index]["status"] = new_status
    if new_end_date:
        quests_data["quests"][quest_index]["end_date"] = new_end_date

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(quests_data, f, ensure_ascii=False, indent=4)

    return jsonify(quests_data["quests"][quest_index])

# クエストの新規作成
@quests_blueprint.route('/users/<int:user_id>/goals/<int:goal_id>/quest', methods=['POST'])
def post_quest(user_id, goal_id):
    title = request.json.get('title')
    description = request.json.get('description')
    end_date = request.json.get('end_date')

    if not title or not description or not end_date:
        return jsonify({"error": "Title, description, and end_date are required."}), 400
    # chats.json ファイルのパスを取得
    file_path = os.path.join(current_app.root_path, 'data','quests.json')

    # chats.json ファイルを読み込む
    with open(file_path, 'r', encoding='utf-8') as file:
        quests = json.load(file)

    # 新しいクエストメッセージを作成
    new_quest = {
        "id": len(quests['quests']) + 1,  # 仮のID生成
        "user_id": user_id,
        "goal_id": goal_id,
        "title": title,
        "description": description,
        "status": 0,
        "end_date": end_date,
        "coins_distributed": False
    }

    # チャットリストに新しいメッセージを追加
    quests['quests'].append(new_quest)

    # 更新されたデータをファイルに書き戻す
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(quests, file, ensure_ascii=False, indent=4)

    return jsonify(new_quest), 201

# クエスト削除
@quests_blueprint.route('/quests/<int:quest_id>', methods=['DELETE'])
def delete_quest(quest_id):
    # quests.json ファイルのパスを取得
    file_path = os.path.join(current_app.root_path, 'data', 'quests.json')

    # quests.json ファイルを読み込む
    with open(file_path, 'r', encoding='utf-8') as file:
        quests = json.load(file)

    # 削除対象のクエストを探す
    quest_to_delete = next((quest for quest in quests['quests'] if quest['id'] == quest_id), None)
    if not quest_to_delete:
        return jsonify({"error": "Quest not found"}), 404

    # クエストを削除
    quests['quests'].remove(quest_to_delete)

    # 更新されたデータをファイルに書き戻す
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(quests, file, ensure_ascii=False, indent=4)

    return jsonify({"message": "Quest deleted successfully"}), 200


@quests_blueprint.route('/users/<int:user_id>/goals/<int:goal_id>/quests/<int:quest_id>/complete', methods=['PATCH']) 
def quest_complete(user_id, goal_id, quest_id):
    file_quests_path = os.path.join(current_app.root_path, 'data', 'quests.json')
    file_coins_path = os.path.join(current_app.root_path, 'data', 'coins.json')
    
    with open(file_quests_path, 'r', encoding="utf-8") as f:
        quests_data = json.load(f)

    # クエストデータをフィルタリング
    quest = next((quest for quest in quests_data["quests"] if quest["user_id"] == user_id and quest["goal_id"] == goal_id and quest["id"] == quest_id), None)

    if not quest:
        return jsonify({"error": "指定されたクエストは存在しない"}), 400

    if quest["status"] == 100 and not quest["coins_distributed"]:
        # コイン配布処理
        with open(file_coins_path, 'r', encoding="utf-8") as f:
            coins_data = json.load(f)

        coins_record = next((coin for coin in coins_data["coins"] if coin["user_id"] == user_id), None)

        if not coins_record:
            return jsonify({"error": "そのユーザーのコインデータは存在しない"}), 400

        coins_record["amount"] += 100  # 仮に報酬を100コインとする
        quest["coins_distributed"] = True  # コイン配布済みに設定

        # データをファイルに書き戻す
        with open(file_coins_path, 'w', encoding='utf-8') as f:
            json.dump(coins_data, f, ensure_ascii=False, indent=4)
    else:
        return jsonify({"error": "クエストはまだ完了していない、またはコインが既に配布されている"}), 400

    with open(file_quests_path, 'w', encoding='utf-8') as f:
        json.dump(quests_data, f, ensure_ascii=False, indent=4)

    return jsonify(quest)
