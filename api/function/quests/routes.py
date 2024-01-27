from flask import Flask, jsonify, current_app,request,Response
import json
import os
from datetime import datetime
from flask import Blueprint, jsonify
import pymysql.cursors
quests_blueprint = Blueprint('quests', __name__)

def get_db_connection():
    return pymysql.connect(host='tutorial.clmkyaosgimn.ap-northeast-1.rds.amazonaws.com',
                    user='admin',
                    db='hackathon_project',
                    charset='utf8mb4',
                    password='OZaKi1030',
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

#クエストの詳細を更新
@quests_blueprint.route('/users/<int:user_id>/goals/<int:goal_id>/quests/<int:quest_id>', methods=['PATCH'])
def quest_edit(user_id, goal_id, quest_id):
    new_title = request.json.get('title')
    new_description = request.json.get('description')
    new_status = request.json.get('status')
    new_end_date = request.json.get('end_date')

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # クエストの詳細を更新するクエリを実行
            query = '''
                UPDATE quests
                SET title = %s, description = %s, status = %s, end_date = %s, coins_distributed=0
                WHERE id = %s
            '''
            cursor.execute(query, (new_title, new_description, new_status, new_end_date, quest_id))

            # データベースの変更をコミット
            conn.commit()

            # 更新されたクエストのデータを取得
            cursor.execute('SELECT * FROM quests WHERE id = %s', (quest_id,))
            updated_quest = cursor.fetchone()

            if updated_quest:
                return jsonify(updated_quest)
            else:
                return jsonify({"error": "指定されたデータは存在しない"}), 404

    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        conn.rollback()  # エラーが発生した場合はロールバック
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()

@quests_blueprint.route('/users/<int:user_id>/goals/<int:goal_id>/quest', methods=['POST'])
def post_quest(user_id, goal_id):
    title = request.json.get('title')
    description = request.json.get('description')
    end_date = request.json.get('end_date')

    if not title or not description or not end_date:
        return jsonify({"error": "Title, description, and end_date are required."}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # quests テーブルに新しいクエストを挿入
            cursor.execute('''
                INSERT INTO quests (title, description, status, end_date,coins_distributed)
                VALUES (%s, %s, %s, %s,0)
            ''', (title, description, 0, end_date))
            quest_id = cursor.lastrowid

            # goal_quests テーブルにクエストと目標の関連を挿入
            cursor.execute('''
                INSERT INTO goal_quests (goal_id, quest_id)
                VALUES (%s, %s)
            ''', (goal_id, quest_id))

            # データベースの変更をコミット
            conn.commit()

            # 新しいクエストのデータを返す
            new_quest = {
                "id": quest_id,
                "title": title,
                "description": description,
                "status": 0,
                "end_date": end_date,
                "coins_distributed": 0
            }
            return jsonify(new_quest), 201

    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        conn.rollback()  # エラーが発生した場合はロールバック
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()
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
