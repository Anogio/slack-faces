from flask import Flask


from api.game_api import game_api
from api.slack_login_api import slack_api

app = Flask(__name__)
app.register_blueprint(game_api)
app.register_blueprint(slack_api)