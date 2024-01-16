from flask import Flask, jsonify, current_app,request,Response
import json
import os
from datetime import datetime
from flask import Blueprint
import pymysql.cursors
import base64

emojis_blueprint = Blueprint('emojis', __name__)
#データベース設定
def get_db_connection():
    return pymysql.connect(host='localhost',
                    user='root',
                    db='hackathon_project',
                    charset='utf8mb4',
                    password='ozaki',
                    cursorclass=pymysql.cursors.DictCursor)

#絵文字のリストを取得
<<<<<<< HEAD
@emojis_blueprint.route('/emojis', methods=['GET'])
def get_emojis():
    # データベース接続を取得
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 絵文字のリストを取得するクエリを実行
            cursor.execute('SELECT * FROM emojis')
            emojis = cursor.fetchall()

            # 結果をJSON形式でクライアントに返却
            return jsonify(emojis)
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()
=======
@emojis_blueprint.route('/emojis', methods = ['GET'], endpoint='get_emojis')
def get_emojis():
    file_path = os.path.join(current_app.root_path, 'data', 'emojis.json')
    
    with open(file_path, 'r', encoding="utf-8") as f:
        emojis_data = json.load(f)
    
    # user_idに基づいてusersをフィルタリングする
    emojis_json = json.dumps(emojis_data, ensure_ascii=False,indent=2)
    
    return Response(emojis_json, content_type='application/json; charset=utf-8')
>>>>>>> e11ac34 (データ変更、APIの書き込みを追加)

@emojis_blueprint.route('/emojis/<int:user_id>', methods=['GET'],endpoint='get_emojis_by_user')
def get_emojis_filtered_users(user_id): 
    file_path = os.path.join(current_app.root_path, 'data', 'user_emojis.json')

    with open(file_path, 'r', encoding="utf-8") as f:
        emojis_data = json.load(f)

    # user_idに基づいて絵文字データをフィルタリング
    filtered_emojis = [emoji for emoji in emojis_data['user_emojis'] if emoji['user_id'] == int(user_id)]

    # 必要なフォーマットに変換
    formatted_emojis = []
    for emoji in filtered_emojis:
        emoji_title = emoji['emoji_id']  # emoji_idに基づいて適切な絵文字タイトルを割り当てる
        formatted_emojis.append({'title': emoji_title, 'date': emoji['date']})

    return jsonify(formatted_emojis)

#ユーザーが記録した絵文字を保存
@emojis_blueprint.route('/users/<int:user_id>/emojis/<int:emoji_id>/record', methods=['POST'])
<<<<<<< HEAD
def record_emoji(user_id, emoji_id):
    # データベース接続を取得
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 現在の日時を取得
            recorded_at = datetime.utcnow()

            # 絵文字記録をデータベースに挿入するクエリを実行
            cursor.execute('INSERT INTO user_emojis (user_id, emoji_id, date) VALUES (%s, %s, %s)', 
                           (user_id, emoji_id, recorded_at))
            
            # 挿入されたレコードのIDを取得
            record_id = cursor.lastrowid

            # データベースの変更をコミット
            conn.commit()

            # 新しい絵文字記録を返す
            return jsonify({
                "id": record_id,
                "user_id": user_id,
                "emoji_id": emoji_id,
                "recorded_at": recorded_at.isoformat() + 'Z'
            }), 201
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        conn.rollback()
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()

=======
def record_emoji(user_id,emoji_id):
    # JSONファイルを読み込む
    try:
        file_path = os.path.join(current_app.root_path, 'data', 'user_emojis.json')
        with open(file_path, 'r') as file:
            data = json.load(file)
    except (IOError, json.JSONDecodeError):
        data = {'user_emojis': []}

    # 新しい絵文字データを作成
    new_emoji_data = {
        "id": len(data['user_emojis']) + 1,  # 新しいIDを生成
        "user_id": user_id,
        "emoji_id": emoji_id,
        "date": datetime.utcnow().isoformat() + 'Z',
    }

    # データを追加
    data['user_emojis'].append(new_emoji_data)

    # ファイルに書き戻す
    try:
        file_path = os.path.join(current_app.root_path, 'data', 'user_emojis.json')
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
    except IOError:
        return jsonify({"error": "Could not save data"}), 500

    # 新しい絵文字データを返す
    return jsonify(new_emoji_data), 201
>>>>>>> e11ac34 (データ変更、APIの書き込みを追加)


#特定の日付に紐づく絵文字データの取得
@emojis_blueprint.route('/users/<int:user_id>/emojis/<string:date>', methods=['GET'])
def get_emoji_filtered_date(user_id, date):
    try:
        correct_date = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
<<<<<<< HEAD
        # 日付の形式が間違えればエラーを返す
        return jsonify({"error": "Incorrect date format, should be YYYY-MM-DD"}), 400
    
    # データベース接続を取得
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 特定の日付に紐づく絵文字データを取得するクエリを実行
            cursor.execute('''
                SELECT ue.id, ue.user_id, ue.emoji_id, ue.date, e.content
                FROM user_emojis ue
                JOIN emojis e ON ue.emoji_id = e.id
                WHERE ue.user_id = %s AND DATE(ue.date) = %s
            ''', (user_id, correct_date.strftime('%Y-%m-%d')))
            emojis = cursor.fetchall()

            # 結果をJSON形式でクライアントに返却
            return jsonify(emojis)
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()

=======
        return jsonify({"error": "Incorrect date format, should be YYYY-MM-DD"}), 400

    file_path = os.path.join(current_app.root_path, 'data', 'user_emojis.json')
    with open(file_path, 'r', encoding="utf-8") as f:
        user_emojis_data = json.load(f)

    filtered_emoji = [
        emoji for emoji in user_emojis_data['user_emojis']
        if emoji['user_id'] == user_id and datetime.strptime(emoji['date'].split('T')[0], '%Y-%m-%d').date() == correct_date
    ]

    return jsonify(filtered_emoji)
>>>>>>> e11ac34 (データ変更、APIの書き込みを追加)

#特定の期間の日付に紐づく絵文字データの取得

@emojis_blueprint.route('/users/<int:user_id>/emojis', methods=['GET'])
def get_emoji_filtered_dateterm(user_id):
    try:
        # クエリパラメータから開始日と終了日を取得
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        # URLから受け取った日付が正しい形式であるか確認する
        correct_startdate = datetime.strptime(start_date, '%Y-%m-%d').date()
        correct_enddate = datetime.strptime(end_date, '%Y-%m-%d').date()

    except ValueError:
        # 日付の形式が間違っていればエラーを返す
        return jsonify({"error": "Incorrect date format, should be YYYY-MM-DD"}), 400
    
    # データベース接続を取得
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 特定の期間に紐づく絵文字データを取得するクエリを実行
            cursor.execute('''
                SELECT ue.id, ue.user_id, ue.emoji_id, ue.date, e.content
                FROM user_emojis ue
                JOIN emojis e ON ue.emoji_id = e.id
                WHERE ue.user_id = %s AND DATE(ue.date) BETWEEN %s AND %s
            ''', (user_id, correct_startdate, correct_enddate))
            emojis = cursor.fetchall()

            # 結果をJSON形式でクライアントに返却
            return jsonify(emojis)

    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()

     

#設定された絵文字の変更
@emojis_blueprint.route('/users/<int:user_id>/emojis/<date>', methods=['PUT'])
def update_emoji(user_id, date):
    new_emoji_id = request.json.get('emoji_id')
    try:
        # URLから受け取った日付が正しい形式であるか確認する
        correct_date = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        # 日付の形式が間違えればエラーを返す
        return jsonify({"error": "Incorrect date format, should be YYYY-MM-DD"}), 400

    # データベース接続を取得
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 特定の日付に紐づく絵文字データを更新するクエリを実行
            update_result = cursor.execute('''
                UPDATE user_emojis 
                SET emoji_id = %s 
                WHERE user_id = %s AND DATE(date) = %s
            ''', (new_emoji_id, user_id, correct_date))

            # データベースの変更をコミット
            conn.commit()

            # 更新が行われたか確認
            if update_result > 0:
                return jsonify({"success": "Emoji updated successfully"}), 200
            else:
                return jsonify({"error": "No emoji was updated"}), 404

    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        conn.rollback()  # エラーが発生した場合はロールバック
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()

