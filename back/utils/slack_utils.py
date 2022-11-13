import requests
from flask import abort
from cachetools import cached, LRUCache

from domain.models import SlackUser
from constants import BOT_TOKEN


def is_human_with_custom_pic(user_payload: dict) -> bool:
    return (
        not user_payload["deleted"]
        and not user_payload["is_bot"]
        and not user_payload["profile"].get("always_active")
        and user_payload["profile"].get("is_custom_image")
    )


def get_slack_users() -> list[SlackUser]:
    response = requests.get(
        "https://slack.com/api/users.list",
        headers={"Authorization": f"Bearer {BOT_TOKEN}"},
    )
    if response.status_code != 200:
        abort(500, "Failed to get Slack users")

    return [
        SlackUser(name=u["real_name"], profile_picture_url=u["profile"][f"image_192"])
        for u in response.json()["members"]
        if is_human_with_custom_pic(u)
    ]


@cached(cache=LRUCache(maxsize=2))
def get_slack_users_cached(timestamp: float):
    # This is just a way to make sure that the slack users.list call is cached but only
    # for the same day. This way, when a new puzzle is generated on the next day the
    # list of users will be queried again
    return get_slack_users()
