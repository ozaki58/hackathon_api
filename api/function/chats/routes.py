from flask import Flask, jsonify, current_app,request,Response
import json
import os
from datetime import datetime
from flask import Blueprint
from openai import OpenAI
from flask_mysqldb import MySQL
from db import conn
import pymysql.cursors


chats_blueprint = Blueprint('chats', __name__)
#目標をgptAPIでタスク分解し、作成されたクエストを保存
@chats_blueprint.route('/users/<int:user_id>/chatbot/generate_quests', methods=['POST'])
def generate_quests(user_id):
    # リクエストから目標を取得
    # OpenAI APIキーを設定する
    client = OpenAI(
        # This is the default and can be omitted
        api_key=('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'),
    )

    goal = request.json.get('goal')
    #目標をデータベースに保存
    
        
    prompt=f"{goal}を複数のタスクに分解して"
    
    response=get_completion(prompt, client)

    # 応答からクエストリストを抽出
    quests = response
    
    
    # 改行文字でクエストを分割
    quests_list = quests.split('\n')
   
    # データベースにクエストを保存
    try:
    # 目標をgoalsテーブルに挿入
        with conn.cursor() as cursor:
            cursor.execute('INSERT INTO goals (content) VALUES (%s)', (goal,))
            conn.commit()
            cursor.execute('SELECT LAST_INSERT_ID() as last_id')  # 列に名前をつける
            result = cursor.fetchone()
            goal_id = result['last_id']

        # ユーザーと目標をuser_goalテーブルに紐づける
        with conn.cursor() as cursor:
            cursor.execute(
                'INSERT INTO user_goals (user_id, goal_id) VALUES (%s, %s)', 
                (user_id, goal_id)
            )
            conn.commit()

        # クエストをquestsテーブルに挿入し、goal_questsテーブルに紐づける
        with conn.cursor() as cursor:
            for quest in quests_list:
                cursor.execute(
                    'INSERT INTO quests (title) VALUES (%s)', 
                    (quest,)
                )
                conn.commit()
                cursor.execute('SELECT LAST_INSERT_ID() as last_id')  # 列に名前をつける
                result = cursor.fetchone()
                quest_id = result['last_id']
                
                cursor.execute(
                    'INSERT INTO goal_quests (goal_id, quest_id) VALUES (%s, %s)',
                    (goal_id, quest_id)
                )
                conn.commit()
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        conn.rollback()  # エラーが発生した場合はロールバック

    finally:
        conn.close()
    
    

    # 生成されたクエストリストをJSON形式で返す
    return jsonify({'quests': quests_list})
    
def get_completion(prompt, client_instance, model="gpt-3.5-turbo-1106"):
  
  messages = [{"role": "user", "content": prompt}]
  response = client_instance.chat.completions.create(
  model=model,
  messages=messages,
  max_tokens=300,
  temperature=0,
  )
  return response.choices[0].message.content







#チャットした文を保存する
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

#チャットの履歴を取得する
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



 