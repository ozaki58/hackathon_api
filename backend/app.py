from flask import Flask, jsonify, current_app,request,Response
import json
import os
from datetime import datetime
app = Flask(__name__)

#特定のユーザーの目標を取得
@app.route('/users/<int:user_id>/goals', methods=['GET'])
def get_user_goals(user_id):
    
    file_path = os.path.join(current_app.root_path, 'data', 'goals.json')
    
    with open(file_path, 'r', encoding="utf-8") as f:
        data = json.load(f)
    
    # goalsのリストをuser_idでフィルタする
    user_goals = [goal for goal in data['goals'] if goal['user_id'] == user_id]
   
    return jsonify(user_goals)

#　目標を登録する
@app.route('/users/<int:user_id>/goals', methods=['POST'])
def set_user_goal(user_id):
    content = request.json.get('content')
     
    if content is None:
        return jsonify({"error": "Content is required."}), 400
    
    new_goal_id = 1 # これはダミーのID。実際はデータベースに対応させる
    
  
    created_at = datetime.utcnow().isoformat() + 'Z'  

    # 新しい目標を作成（実際のアプリではデータベースに保存する）
    new_goal = {
        "id": new_goal_id,
        "content": content,
        "created_at": created_at
    }
    
    # 新しい目標を返す
    return jsonify(new_goal), 201

@app.route('/users/<int:user_id>/goals/<int:goal_id>/quests', methods=['GET'])
def get_quests_for_goal(user_id, goal_id):

    file_path = os.path.join(current_app.root_path, 'data', 'quests.json')
    
    with open(file_path, 'r', encoding="utf-8") as f:
        quests_data = json.load(f)
    
    # goal_idに基づいてクエストをフィルタリングする
    filtered_quests = [quest for quest in quests_data["quests"] if quest["goal_id"] == goal_id]
    
    quests_json = json.dumps(filtered_quests, ensure_ascii=False,indent=2)
    
    return Response(quests_json, content_type='application/json; charset=utf-8')

#クエストの詳細を取得
@app.route('/quests/<int:quest_id>', methods=['GET'])
def get_quest(quest_id):
    
    file_path = os.path.join(current_app.root_path, 'data', 'quests.json')
    
    with open(file_path, 'r', encoding="utf-8") as f:
        data = json.load(f)
    
    quest = [quest for quest in data["quests"] if quest["id"] == quest_id]
    
    quest_json = json.dumps(quest, ensure_ascii=False,indent=2)
    
    return Response(quest_json, content_type='application/json; charset=utf-8')
   

if __name__ == '__main__':
    app.run(debug=True)


