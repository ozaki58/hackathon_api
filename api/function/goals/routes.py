from flask import Flask, jsonify, current_app,request,Response
import json
import os
from datetime import datetime
from flask import Blueprint
import pymysql.cursors
import base64
from openai import OpenAI

goals_blueprint = Blueprint('goals', __name__)
#データベース設定

def get_db_connection():
    return pymysql.connect(host='tutorial.clmkyaosgimn.ap-northeast-1.rds.amazonaws.com',
                    user='admin',
                    db='hackathon_project',
                    charset='utf8mb4',
                    password='OZaKi1030',
                    cursorclass=pymysql.cursors.DictCursor)


#　目標をgptAPIで深める
@goals_blueprint.route('/users/<int:user_id>/chat_goal', methods=['POST'])
def chat_goal(user_id):
    client = OpenAI(
        api_key=('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'),
    )

    # ユーザーからのチャット入力を受け取る
    user_chat = request.json.get('user_chat')
    user_chat_content = user_chat.get('content')
    
    current_app.logger.info(user_chat_content)
    content = request.json.get('content')
    chat_register(user_id,user_chat_content,0)

    # GPTモデルを使って目標の深掘り
    gpt_response, is_goal_ready = refine_goal_with_chat(user_id,content, client)
    
    chat_register(user_id,gpt_response,1)
    # 応答をJSON形式で返す
    return jsonify({
        'gpt_response': gpt_response,
        'is_goal_ready': is_goal_ready
    })


def chat_register(user_id,content,sender_type):
    conn = get_db_connection()
#　チャットをでデータベースに保存
    try:
        with conn.cursor() as cursor:
            # 現在の日時を取得
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # チャットをデータベースに挿入
            cursor.execute(
                "INSERT INTO goal_chats (user_id, content, created_at, sender_type) VALUES (%s, %s, %s, %s)",
                (user_id, content, now, sender_type)
            )
            conn.commit()
            
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        conn.rollback()  # エラーが発生した場合はロールバック
    finally:
        conn.close()


def refine_goal_with_chat(user_id,chat_input, client_instance):
    # GPTモデルを使ってチャット形式で目標を深掘りするロジックを実装
    client = OpenAI(
        api_key=('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'),
    )
    # ユーザーの入力と過去のチャットからなるプロンプトを作成
    prompt = '目標が送られてきます。もっと詳細な目標に近づくために深掘りをしてください。相手に質問することがなければ、最終的な目標を20字以内で短くまとめてこれで登録しますがよろしいですか？と送ってください。必ず、日本語で返してください。褒めながら進めてください。'
    
    prompt += chat_input

    # GPTモデルに問い合わせ
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    current_app.logger.info(response)

    # GPTモデルからの応答を解析
    gpt_response = response.choices[0].message.content

    # 目標が確定したかどうかを判断するロジックを実装
    is_goal_ready = check_if_goal_is_ready(gpt_response)  
    # 洗練された目標と目標が確定したかどうかのブール値を返す
    return  gpt_response,is_goal_ready


def extract_refined_goal(gpt_response):
    """
    GPTモデルからの応答から洗練された目標の部分のみを抽出する。

    :param gpt_response: GPTモデルからの応答
    :return: 洗練された目標のテキスト
    """
    # 応答から洗練された目標を抽出するロジックを実装
    # 例: 応答を解析して、目標に関連する文を抽出
    # ここでは簡単な例として、特定のフレーズで始まる行を探す
    lines = gpt_response.split('\n')
    for line in lines:
        if "最終的な目標：" in line or "これで登録しますがよろしいですか" in line:
            return line  # 洗練された目標を含む行を返す
    return ""  # 適切な行が見つからない場合


def check_if_goal_is_ready(gpt_response):
    """
    GPTモデルからの応答を分析して、目標が現実的かつ具体的になっているかを判断する。

    :param gpt_response: GPTモデルからの応答
    :return: 目標が確定しているかどうかのブール値
    """
    # 定義するキーワードやフレーズ
    key_phrases = ["これで登録しますがよろしいですか", "最終的な目標"]

    # 応答の中でキーワードやフレーズが見つかったかをチェック
    for phrase in key_phrases:
        if phrase in gpt_response:
            return True

    # キーワードやフレーズが見つからなかった場合は、目標がまだ確定していないと判断
    return False



#特定のユーザー目標チャットを取得
@goals_blueprint.route('/users/<int:user_id>/goal_chats', methods=['GET'])
def get_goal_chats(user_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM goal_chats WHERE user_id = %s', (user_id,))
            chats = cursor.fetchall()
        return jsonify(chats),201
    
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()

#特定のユーザーの目標を取得
@goals_blueprint.route('/users/<int:user_id>/goals', methods=['GET'])
def get_user_goals(user_id):
    # データベース接続を取得
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 特定のユーザーに関連する目標を取得するクエリを実行
            cursor.execute('''
                SELECT g.id, g.content
                FROM goals g
                JOIN user_goals ug ON g.id = ug.goal_id
                WHERE ug.user_id = %s
            ''', (user_id,))
            goals = cursor.fetchall()

            # 結果をJSON形式でクライアントに返却
            return jsonify(goals)
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()

#特定の目標を取得
@goals_blueprint.route('/goals/<int:goal_id>', methods=['GET'])
def get_goals(goal_id):
    # データベース接続を取得
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 特定のユーザーに関連する目標を取得するクエリを実行
            cursor.execute('''
                SELECT content
                FROM goals
                WHERE id = %s
            ''', (goal_id,))
            goals = cursor.fetchall()

            # 結果をJSON形式でクライアントに返却
            return jsonify(goals)
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()
        

#　目標を登録する
@goals_blueprint.route('/users/<int:user_id>/goals', methods=['POST'])
def set_user_goal(user_id):
    content = request.json.get('content')
    if content is None:
        return jsonify({"error": "Content is required."}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 新しい目標をデータベースに挿入するクエリを実行
            cursor.execute('INSERT INTO goals (content) VALUES (%s)', (content,))
            # 挿入された目標のIDを取得
            new_goal_id = cursor.lastrowid
            conn.commit()

            # user_goal テーブルにレコードを挿入
            cursor.execute('INSERT INTO user_goals (user_id, goal_id) VALUES (%s, %s)', (user_id, new_goal_id))
            conn.commit()

            # 新しい目標とユーザーの関係を返す
            new_user_goal = {
                "id": cursor.lastrowid,
                "user_id": user_id,
                "goal_id": new_goal_id,
                "content": content
            }
            return jsonify(new_user_goal), 201
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        conn.rollback()
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()

