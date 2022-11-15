from flask import request, abort, Blueprint, jsonify
import jwt
from slack_sdk.web import WebClient
from slack_sdk.oauth import OpenIDConnectAuthorizeUrlGenerator
from slack_sdk.oauth.state_store import FileOAuthStateStore

from constants import SLACK_CLIENT_ID, SLACK_CLIENT_SECRET

state_store = FileOAuthStateStore(expiration_seconds=300)
scopes = ["openid", "profile"]


slack_api = Blueprint("slack_api", __name__)


@slack_api.route("/slack/login", methods=["GET"])
def oauth_start():
    if "redirect_uri" not in request.args:
        abort(400, "Missing parameter redirect_uri")

    authorization_url_generator = OpenIDConnectAuthorizeUrlGenerator(
        client_id=SLACK_CLIENT_ID,
        scopes=scopes,
        redirect_uri=request.args["redirect_uri"],
    )
    state = state_store.issue()
    url = authorization_url_generator.generate(state=state)
    result = jsonify({"redirect_url": url})
    result.headers.add("Access-Control-Allow-Origin", "*")
    return result


@slack_api.route("/slack/oauth_redirect", methods=["GET"])
def oauth_callback():
    if "code" not in request.args:
        abort(400, "Missing parameter code")
    if "state" not in request.args:
        abort(400, "Missing parameter state")
    state = request.args["state"]

    if state_store.consume(state):
        code = request.args["code"]
        try:
            token_response = WebClient().openid_connect_token(
                client_id=SLACK_CLIENT_ID, client_secret=SLACK_CLIENT_SECRET, code=code
            )
            print(f"openid.connect.token response: {token_response}")
            id_token = token_response.get("id_token")
            claims = jwt.decode(
                id_token, options={"verify_signature": False}, algorithms=["RS256"]
            )
            print(f"claims (decoded id_token): {claims}")

            user_token = token_response.get("access_token")
            user_info_response = WebClient(token=user_token).openid_connect_userInfo()
            print(f"openid.connect.userInfo response: {user_info_response}")
            return "SUCCESS"

        except Exception:
            print("Failed to perform openid.connect.token API call")
            abort(500, "Failed to perform openid.connect.token API call")
    else:
        return abort(500, "The state value is already expired")
