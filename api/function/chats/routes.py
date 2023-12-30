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
                (user_id, character_id, content, 1)
            )
            conn.commit()

        # チャットボットのレスポンスを保存
        with conn.cursor() as cursor:
            cursor.execute(
                'INSERT INTO chats (user_id, character_id, content, sender_type) VALUES (%s, %s, %s, %s)',
                (user_id, character_id, chatbot_response, 0)
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
        "sender_type": 0  # キャラ
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
