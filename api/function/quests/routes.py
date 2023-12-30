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
def quest_edit(user_id, goal_id, quest_id):
    # リクエストから更新するデータを取得
    new_title = request.json.get('title')
    new_description = request.json.get('description')
    new_status = request.json.get('status')
    new_end_date = request.json.get('end_date')

    # データベース接続を開始
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # クエリのパーツを格納するリスト
            update_parts = []
            update_values = []
            
            # 各フィールドについて更新する値があれば、クエリのパーツを追加
            if new_title:
                update_parts.append('q.title = %s')
                update_values.append(new_title)
            if new_description:
                update_parts.append('q.description = %s')
                update_values.append(new_description)
            if new_status is not None:
                update_parts.append('q.status = %s')
                update_values.append(new_status)
            if new_end_date:
                update_parts.append('q.end_date = %s')
                update_values.append(new_end_date)
            
            # 更新する値がある場合にのみクエリを実行
                
            # 更新する値がある場合にのみクエリを実行
            if update_parts:
                # クエリの文字列を組み立て
                update_string = ', '.join(update_parts)
                update_values.append(user_id)
                update_values.append(goal_id)
                update_values.append(quest_id)

                # クエリを実行
                cursor.execute(f'''
                    UPDATE quests q
                    INNER JOIN goal_quests gq ON q.id = gq.quest_id
                    INNER JOIN user_goals ug ON gq.goal_id = ug.goal_id
                    SET {update_string}
                    WHERE ug.user_id = %s AND ug.goal_id = %s AND q.id = %s
                ''', update_values)

                
                conn.commit()

                # 更新されたクエストを取得
                cursor.execute('SELECT * FROM quests WHERE id = %s', (quest_id))
                updated_quest = cursor.fetchone()
                return jsonify(updated_quest) if updated_quest else ('', 404)
            else:
                return jsonify({"error": "No update parameters provided"}), 400
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        conn.rollback()
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()

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
