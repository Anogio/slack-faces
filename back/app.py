import flask
from flask import Flask
from flask import abort, request, send_file
from flask_cors import cross_origin
import requests
import random
import datetime as dt
from PIL import Image
from io import BytesIO
from cachetools import cached, LRUCache
import encryption_utils
from constants import NameMatch, QUESTIONS_PER_DAY, IMAGE_RESOLUTIONS, BOT_TOKEN


app = Flask(__name__)


@app.route("/puzzle", methods=["GET"])
def puzzle():
    datetime_today = dt.datetime.combine(dt.date.today(), dt.time(0, 0, 0)).timestamp()
    todays_puzzle_keys, all_names = get_day_puzzle(timestamp=datetime_today)
    result = flask.jsonify({"puzzle_keys": todays_puzzle_keys, "all_names": all_names})
    result.headers.add("Access-Control-Allow-Origin", "*")
    return result


@app.route("/pixelated_image", methods=["GET"])
def pixelated_image():
    args = request.args
    if "puzzle_key" not in args:
        abort(400, "Missing parameter puzzle_key")

    puzzle_key = args["puzzle_key"]
    pixelated = get_image_from_puzzle_key(puzzle_key)
    img_io = BytesIO()
    pixelated.save(img_io, "JPEG", quality=100)
    img_io.seek(0)
    result = send_file(img_io, mimetype="image/jpeg")
    return result


@app.route("/submit", methods=["POST"])
@cross_origin()
def submit():
    payload = request.json
    assert isinstance(payload, list)
    assert len(payload) == QUESTIONS_PER_DAY

    puzzles = [encryption_utils.decrypt_dict(guess["puzzle_key"]) for guess in payload]
    true_names = [puzzle["name"] for puzzle in puzzles]

    results = []
    for i, guess in enumerate(payload):
        puzzle = puzzles[i]
        true_name = puzzle["name"]
        guessed_name = guess["name"]

        match = (
            NameMatch.EXACT_MATCH
            if true_name == guessed_name
            else NameMatch.PARTIAL_MATCH
            if guessed_name in true_names
            else NameMatch.NO_MATCH
        )

        # If puzzle is won, show full image, otherwise lower the pixelation one step
        new_resolution = (
            len(IMAGE_RESOLUTIONS) - 1
            if match == NameMatch.EXACT_MATCH
            else min(puzzle["resolution_rank"] + 1, len(IMAGE_RESOLUTIONS) - 1)
        )
        results.append(
            {
                "match": match.value,
                "puzzle_key": encryption_utils.encrypt_dict(
                    {**puzzle, "resolution_rank": new_resolution}
                ),
            }
        )
    return results


def get_downscaled_image(image_url: str, target_resolution: int) -> Image:
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    imgSmall = img.resize(
        (target_resolution, target_resolution), resample=Image.BILINEAR
    )
    pixelated = imgSmall.resize(img.size, Image.NEAREST)
    return pixelated


@cached(cache=LRUCache(maxsize=1024))
def get_image_from_puzzle_key(puzzle_key: str) -> Image:
    puzzle = encryption_utils.decrypt_dict(puzzle_key)
    target_resolution = IMAGE_RESOLUTIONS[puzzle["resolution_rank"]]
    image_url = puzzle["image_url"]
    pixelated = get_downscaled_image(image_url, target_resolution)

    return pixelated


@cached(cache=LRUCache(maxsize=2))
def get_day_puzzle(timestamp: float) -> tuple[list[str], list[str]]:
    response = requests.get(
        "https://slack.com/api/users.list",
        headers={"Authorization": f"Bearer {BOT_TOKEN}"},
    )
    if response.status_code != 200:
        abort(500, "Failed to get Slack users")

    users = [
        {"name": u["real_name"], "image_url": u["profile"][f"image_192"]}
        for u in response.json()["members"]
        if not u["deleted"]
        and not u["is_bot"]
        and not u["profile"].get("always_active")
        and u["profile"].get("is_custom_image")
    ]

    random.seed(timestamp)
    todays_puzzle_users = random.sample(population=users, k=QUESTIONS_PER_DAY)
    todays_puzzle_keys = [
        encryption_utils.encrypt_dict(
            {"name": u["name"], "image_url": u["image_url"], "resolution_rank": 0}
        )
        for u in todays_puzzle_users
    ]

    return todays_puzzle_keys, sorted([u["name"] for u in users])
