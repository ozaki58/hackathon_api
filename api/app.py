from flask import Flask, jsonify, current_app,request,Response
import json
import os
from datetime import datetime

from function.goals.routes import goals_blueprint
from function.quests.routes import quests_blueprint
from function.users.routes import users_blueprint
from function.characters.routes import characters_blueprint
from function.emojis.routes import emojis_blueprint
from function.chats.routes import chats_blueprint
from flask_mysqldb import MySQL


# MySQLデータベース設定
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

app.register_blueprint(goals_blueprint)
app.register_blueprint(quests_blueprint)
app.register_blueprint(users_blueprint)
app.register_blueprint(characters_blueprint)
app.register_blueprint(emojis_blueprint)
app.register_blueprint(chats_blueprint)




@app.route('/some_path')
def some_function():
    return {'some_key': 'some_value'}

if __name__ == '__main__':
    app.run(debug=True)




