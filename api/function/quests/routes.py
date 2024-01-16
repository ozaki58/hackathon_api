from flask import Flask, jsonify, current_app,request,Response
import json
import os
from datetime import datetime
from flask import Blueprint, jsonify
import pymysql.cursors
quests_blueprint = Blueprint('quests', __name__)

#データベース設定
def get_db_connection():
    return pymysql.connect(host='localhost',
                    user='root',
                    db='hackathon_project',
                    charset='utf8mb4',
                    password='ozaki',
                    cursorclass=pymysql.cursors.DictCursor)

#目標に紐づくクエストリストの取得

@quests_blueprint.route('/users/<int:user_id>/goals/<int:goal_id>/quests', methods=['GET'])
def get_quests_for_goal(user_id,goal_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # user_goal、goal_quests、および quests テーブルを結合する
            cursor.execute('''
                SELECT q.* FROM quests AS q
                INNER JOIN goal_quests AS gq ON q.id = gq.quest_id
                INNER JOIN user_goals AS ug ON gq.goal_id = ug.goal_id
                WHERE ug.user_id = %s AND ug.goal_id = %s
            ''', (user_id, goal_id))
            quests = cursor.fetchall()
        return jsonify(quests)
    finally:
        conn.close()
    
    

#クエストの詳細を取得
@quests_blueprint.route('/quests/<int:quest_id>', methods=['GET'])
def get_quest(quest_id):
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM quests WHERE id = %s', (quest_id,))
            quest = cursor.fetchone()
        return jsonify(quest) if quest else ('', 404)
    finally:
        conn.close()

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
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # クエストが存在するか確認
        cursor.execute('SELECT * FROM quests WHERE id = %s', (quest_id,))
        quest = cursor.fetchone()
        if quest is None:
            return make_response(jsonify({"error": "Quest not found"}), 404)

        # クエストを削除
        cursor.execute('DELETE FROM quests WHERE id = %s', (quest_id,))
        conn.commit()
        
        return make_response(jsonify({"message": "Quest deleted successfully"}), 200)
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        conn.rollback()
        return jsonify({"error": "Database error"}), 500
    finally:
        cursor.close()
        conn.close()

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
