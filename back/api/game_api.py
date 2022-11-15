import flask
from flask import abort, request, Blueprint
from flask_cors import cross_origin

from constants import QUESTIONS_PER_DAY, N_TRIES_ALLOWED
from utils import image_utils
from domain.models import GameState
from domain import game_logic


game_api = Blueprint("game_api", __name__)


@game_api.route("/start_game", methods=["GET"])
def start_game():
    initial_game_state, all_names = game_logic.get_initial_game_state_and_options()

    result = flask.jsonify(
        {
            "game_state": initial_game_state.to_encrypted_string(),
            "all_names": all_names,
            "max_tries": N_TRIES_ALLOWED,
            "n_pictures": QUESTIONS_PER_DAY,
        }
    )

    result.headers.add("Access-Control-Allow-Origin", "*")
    return result


@game_api.route("/guessable_picture", methods=["GET"])
def pixelated_image():
    args = request.args
    if "game_state" not in args:
        abort(400, "Missing parameter puzzle_key")
    if "picture_index" not in args:
        abort(400, "Missing parameter image_index")

    print("STATE: ", args["game_state"])
    game_state = GameState.from_encrypted_string(encrypted_string=args["game_state"])
    picture_index = int(args["picture_index"])
    if picture_index < 0 or picture_index >= QUESTIONS_PER_DAY:
        abort(400, "Invalid image_index")

    picture_to_guess = game_logic.get_picture_to_guess(
        game_state=game_state, picture_index=picture_index
    )
    return image_utils.send_picture_file(picture_to_guess)


@game_api.route("/submit", methods=["POST"])
@cross_origin()
def submit():
    payload = request.json
    if "game_state" not in payload:
        abort(400, "Missing parameter puzzle_key")
    if "guesses" not in payload:
        abort(400, "Missing parameter puzzle_key")

    game_state = GameState.from_encrypted_string(encrypted_string=payload["game_state"])
    if game_state.game_finished:
        abort(400, "This game is already finished")

    guesses = payload["guesses"]
    if (
        not isinstance(guesses, list)
        or not all(isinstance(el, str) for el in guesses)
        or len(guesses) != QUESTIONS_PER_DAY
    ):
        abort(400, "Parameter guesses is invalid")

    matches, new_game_state = game_logic.handle_submit(
        game_state=game_state, guesses=guesses
    )
    return {
        "game_state": new_game_state.to_encrypted_string(),
        "matches": [match.value for match in matches],
        "solution": [u.name for u in new_game_state.users_to_guess]
        if new_game_state.game_finished
        else [],
    }
