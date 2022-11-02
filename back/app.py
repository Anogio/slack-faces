import flask
from flask import Flask
from flask import abort
import requests
import random
import datetime as dt
app = Flask(__name__)

QUESTIONS_PER_DAY = 5

with open("bot_token.txt") as f:
    BOT_TOKEN = f.readlines()[0]


@app.route("/puzzle")
def puzzle():
    response = requests.get("https://slack.com/api/users.list", headers={"Authorization": f"Bearer {BOT_TOKEN}"})
    if response.status_code != 200:
        abort(500, "Failed to get Slack users")

    response_json = response.json()
    users = [{"name": u["real_name"], "picture": u["profile"]["image_192"]} for u in response_json["members"]
             if not u["deleted"] and not u["is_bot"]  and not u["profile"].get("always_active")
             and u["profile"].get("is_custom_image")]

    datetime_today = dt.datetime.combine(dt.date.today(), dt.time(0, 0, 0)).timestamp()
    random.seed(datetime_today)
    todays_puzzle = random.sample(population=users, k=QUESTIONS_PER_DAY)
    result = flask.jsonify({
        "puzzle": todays_puzzle,
        "all_names": sorted([u["name"] for u in users])
    })
    result.headers.add('Access-Control-Allow-Origin', '*')
    return result
