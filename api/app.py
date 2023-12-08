from flask import Flask, jsonify, current_app,request,Response
import json
import os
from datetime import datetime

from function.goals.routes import goals_blueprint
from function.quests.routes import quests_blueprint

app = Flask(__name__)


app.register_blueprint(goals_blueprint)
app.register_blueprint(quests_blueprint)

if __name__ == '__main__':
    app.run(debug=True)



