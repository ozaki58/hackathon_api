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
    filtered_quests = [quest for quest in quests_data["quests"] if quest["goal_id"] == goal_id]
    
    quests_json = json.dumps(filtered_quests, ensure_ascii=False,indent=2)
    
    return Response(quests_json, content_type='application/json; charset=utf-8')

#クエストの詳細を取得
@quests_blueprint.route('/quests/<int:quest_id>', methods=['GET'])
def get_quest(quest_id):
    
    file_path = os.path.join(current_app.root_path, 'data', 'quests.json')
    
    with open(file_path, 'r', encoding="utf-8") as f:
        data = json.load(f)
    
    quest = [quest for quest in data["quests"] if quest["id"] == quest_id]
    
    quest_json = json.dumps(quest, ensure_ascii=False,indent=2)
    
    return Response(quest_json, content_type='application/json; charset=utf-8')
   

