import flask
from flask import Flask
from flask import abort
import requests
import random
import datetime as dt
from cachetools import cached, LRUCache

app = Flask(__name__)

QUESTIONS_PER_DAY = 5

with open("bot_token.txt") as f:
    BOT_TOKEN = f.readlines()[0]


@app.route("/puzzle")
def puzzle():
    datetime_today = dt.datetime.combine(dt.date.today(), dt.time(0, 0, 0)).timestamp()
    todays_puzzle, users = get_day_puzzle(timestamp=datetime_today)
    result = flask.jsonify(
        {"puzzle": todays_puzzle, "all_names": sorted([u["name"] for u in users])}
    )
    result.headers.add("Access-Control-Allow-Origin", "*")
    return result


@cached(cache=LRUCache(maxsize=2))
def get_day_puzzle(timestamp: float) -> tuple[list, list]:
    response = requests.get(
        "https://slack.com/api/users.list",
        headers={"Authorization": f"Bearer {BOT_TOKEN}"},
    )
    if response.status_code != 200:
        abort(500, "Failed to get Slack users")
    response_json = response.json()
    users = [
        {
            "name": u["real_name"],
            "pictures": [
                u["profile"][f"image_{resolution}"]
                for resolution in [24, 32, 48, 72, 192]
            ],
        }
        for u in response_json["members"]
        if not u["deleted"]
        and not u["is_bot"]
        and not u["profile"].get("always_active")
        and u["profile"].get("is_custom_image")
    ]
    random.seed(timestamp)
    todays_puzzle = random.sample(population=users, k=QUESTIONS_PER_DAY)
    return todays_puzzle, users
