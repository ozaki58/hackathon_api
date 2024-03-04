from flask import Flask, jsonify, current_app,request,Response,Blueprint
import json
import os
from flask import current_app
from datetime import datetime
import pymysql.cursors
import pymysql
from openai import OpenAI

chats_blueprint = Blueprint('chats', __name__)

# #データベース設定
# def get_db_connection():
#     return pymysql.connect(host='tutorial.clmkyaosgimn.ap-northeast-1.rds.amazonaws.com',
#                     user='admin',
#                     db='hackathon_project',
#                     charset='utf8mb4',
#                     password='OZaKi1030',
#                     cursorclass=pymysql.cursors.DictCursor)

def get_db_connection():
    return pymysql.connect(host='localhost',
                    user='root',
                    db='hackathon_project',
                    charset='utf8mb4',
                    password='ozaki',
                    cursorclass=pymysql.cursors.DictCursor)
#目標をgptAPIでタスク分解し、作成されたクエストを保存

@chats_blueprint.route('/goals/<int:goal_id>/chatbot/generate_quests', methods=['POST'])
def generate_quests(goal_id):
    # データベース設定。リクエストごとに定義しないと連続したcrudができない。(最後にコネクションを閉じるため)
    conn = get_db_connection()
    
    # リクエストから目標を取得
    # OpenAI APIキーを設定する
    client = OpenAI(
        api_key=('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'),
    )
    goal = request.json.get('goal')
    #目標をデータベースに保存
    
        
    prompt=f"{goal}を複数のタスクに15字以内で5~10個に分解して"
    
    response=get_completion_quest(prompt,client)

    # 応答からクエストリストを抽出
    quests = response
    # 改行文字でクエストを分割
    quests_list = quests.split('\n')
    # 生成されたクエストリストをJSON形式で返す
    return jsonify({'quests': quests_list})

def get_completion_quest(prompt, client_instance, model="gpt-3.5-turbo-1106"):
  messages = [{"role": "user", "content": prompt}]
  response = client_instance.chat.completions.create(
  model=model,
  messages=messages,
  max_tokens=300,
  temperature=0,
  )
  return response.choices[0].message.content

@chats_blueprint.route('/goals/<int:goal_id>/chatbot/register_quests', methods=['POST'])
def quest_register(goal_id):
    # リクエストからクエストリストを取得
    quests_list = request.json.get('quests')
    if not quests_list:
        return jsonify({"error": "Quests are required"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            for quest in quests_list:
                cursor.execute(
                    'INSERT INTO quests (title) VALUES (%s)', 
                    (quest,)
                )
                conn.commit()
                quest_id = cursor.lastrowid
                
                cursor.execute(
                    'INSERT INTO goal_quests (goal_id, quest_id) VALUES (%s, %s)',
                    (goal_id, quest_id)
                )
                conn.commit()
                
        return jsonify({"message": "Quests registered successfully"}), 201
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        conn.rollback()
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()


#チャットした文とそれに対する返信を保存する
@chats_blueprint.route('/users/<int:user_id>/characters/<int:character_id>/chat', methods=['POST'])
def post_chat(user_id, character_id):
    conn = get_db_connection()
    client = OpenAI(
        api_key=('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'),
    )
    # リクエストからユーザーのメッセージと送信者タイプを取得
    content = request.json.get('content')
    # OpenAIのAPIを使用してレスポンスを生成
    prompt = content  # または過去の対話を含めたプロンプト
    response=get_completion(prompt, client, user_id,character_id)

    # OpenAIのレスポンスからテキストを取得
    chatbot_response = response

    # ユーザーのチャットとそれに対するレスポンスをデータベースに保存する）
    try:
        # ユーザーのチャットを保存
        with conn.cursor() as cursor:
            cursor.execute(
                'INSERT INTO chats (user_id, character_id, content, sender_type) VALUES (%s, %s, %s, %s)',
                (user_id, character_id, content, 0)
            )
            conn.commit()

        # チャットボットのレスポンスを保存
        with conn.cursor() as cursor:
            cursor.execute(
                'INSERT INTO chats (user_id, character_id, content, sender_type) VALUES (%s, %s, %s, %s)',
                (user_id, character_id, chatbot_response, 1)
            )
            conn.commit()

    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        conn.rollback()  # エラーが発生した場合はロールバック

    finally:
        conn.close()
    # チャットボットのレスポンスを含む新しいチャットを返す
    new_chat = {
        # 実際のIDをデータベースから取得
        "user_id": user_id,
        "character_id": character_id,
        "content": chatbot_response,  # チャットボットのレスポンス
        "created_at": datetime.utcnow().isoformat() + 'Z',
        "sender_type": 1  # キャラ
    }
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
    conn = get_db_connection()
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
    conn = get_db_connection()
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

# 特定のユーザー、キャラクター、日付に基づいたメッセージを取得するエンドポイント
@chats_blueprint.route('/users/<int:user_id>/characters/<int:character_id>/date/<int:year>/<int:month>/<int:day>', methods=['GET'])
def get_messages(user_id, character_id, year, month, day):
    # 日付を YYYY-MM-DD 形式に変換
    formatted_date = datetime(year, month, day).strftime('%Y-%m-%d')

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # ここに適切なSQLクエリを記述
            cursor.execute('SELECT * FROM chats WHERE user_id = %s AND character_id = %s AND DATE(created_at) = %s', (user_id, character_id, formatted_date))
            messages = cursor.fetchall()

        return jsonify(messages)
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()

@chats_blueprint.route('/users/<int:user_id>/date/<int:year>/<int:month>/<int:day>', methods=['GET'])
def get_message_character(user_id, year,month,day):
    # 日付のフォーマットを確認し、必要に応じて変換
    try:
        # 日付を YYYY-MM-DD 形式に変換
        formatted_date = datetime(year, month, day).strftime('%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM chats WHERE user_id = %s AND DATE(created_at) = %s', (user_id, formatted_date))
            messages = cursor.fetchall()

        return jsonify(messages)
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()