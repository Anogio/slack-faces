import dataclasses
import datetime as dt

from PIL import Image

from constants import IMAGE_RESOLUTIONS, N_TRIES_ALLOWED
from domain.models import GameState, NameMatch
from utils import slack_utils, image_utils


def get_initial_game_state_and_options() -> tuple[GameState, list[str]]:
    timestamp_today = dt.datetime.combine(dt.date.today(), dt.time(0, 0, 0)).timestamp()
    slack_users = slack_utils.get_slack_users_cached(timestamp=timestamp_today)
    return GameState.initial_state(
        timestamp=timestamp_today, slack_users=slack_users
    ), [u.name for u in slack_users]


def get_picture_to_guess(game_state: GameState, picture_index: int) -> Image:
    user_to_guess = game_state.users_to_guess[picture_index]
    target_resolution = IMAGE_RESOLUTIONS[
        -1
        if user_to_guess.guessed
        else min(game_state.n_submitted_guesses, N_TRIES_ALLOWED - 1)
    ]
    picture_url = user_to_guess.profile_picture_url
    return image_utils.get_downscaled_image(
        image_url=picture_url, target_resolution=target_resolution
    )


def handle_submit(
    game_state: GameState, guesses: list[str]
) -> tuple[list[NameMatch], GameState]:
    assert len(guesses) == len(game_state.users_to_guess)

    all_names_to_guess = [utg.name for utg in game_state.users_to_guess]
    matches = []
    updated_users_to_guess = []
    for user_to_guess, guessed_name in zip(game_state.users_to_guess, guesses):
        if user_to_guess.name == guessed_name:
            matches.append(NameMatch.EXACT_MATCH)
            updated_users_to_guess.append(
                dataclasses.replace(user_to_guess, guessed=True)
            )

        elif guessed_name in all_names_to_guess:
            matches.append(NameMatch.PARTIAL_MATCH)
            updated_users_to_guess.append(user_to_guess)
        else:
            matches.append(NameMatch.NO_MATCH)
            updated_users_to_guess.append(user_to_guess)

    new_game_state = dataclasses.replace(
        game_state,
        n_submitted_guesses=game_state.n_submitted_guesses + 1,
        users_to_guess=updated_users_to_guess,
    )
    return matches, new_game_state
