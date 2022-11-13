import dataclasses
import uuid
from enum import Enum
from uuid import UUID
import random
from constants import QUESTIONS_PER_DAY, N_TRIES_ALLOWED

from utils import encryption_utils


class NameMatch(Enum):
    EXACT_MATCH = "exact"
    PARTIAL_MATCH = "partial"
    NO_MATCH = "none"


@dataclasses.dataclass
class SlackUser:
    name: str
    profile_picture_url: str


@dataclasses.dataclass
class GuessableSlackUser(SlackUser):
    guessed: bool

    @classmethod
    def from_slack_user(cls, slack_user: SlackUser) -> "GuessableSlackUser":
        return cls(
            name=slack_user.name,
            profile_picture_url=slack_user.profile_picture_url,
            guessed=False,
        )


@dataclasses.dataclass
class GameState:
    timestamp: float
    game_uuid: UUID
    users_to_guess: list[GuessableSlackUser]
    n_submitted_guesses: int

    def to_encrypted_string(self) -> str:
        gs_dict = dataclasses.asdict(self)
        gs_dict["game_uuid"] = str(gs_dict["game_uuid"])
        return encryption_utils.encrypt_dict(gs_dict)

    @classmethod
    def from_encrypted_string(cls, encrypted_string: str) -> "GameState":
        gs_dict = encryption_utils.decrypt_dict(encrypted_string)
        gs_dict["game_uuid"] = UUID(gs_dict["game_uuid"])
        gs_dict["users_to_guess"] = [
            GuessableSlackUser(**u) for u in gs_dict["users_to_guess"]
        ]
        return cls(**gs_dict)

    @classmethod
    def initial_state(
        cls, timestamp: float, slack_users: list[SlackUser]
    ) -> "GameState":
        # Sort the users to ensure determinism is not dependent on Slack API ordering
        slack_users = sorted(slack_users, key=lambda x: x.name)
        random.seed(timestamp)
        users_to_guess = random.sample(population=slack_users, k=QUESTIONS_PER_DAY)
        return cls(
            timestamp=timestamp,
            game_uuid=uuid.uuid4(),
            users_to_guess=[
                GuessableSlackUser.from_slack_user(u) for u in users_to_guess
            ],
            n_submitted_guesses=0,
        )

    @property
    def game_won(self) -> bool:
        return all(user.guessed for user in self.users_to_guess)

    @property
    def game_finished(self) -> bool:
        return self.game_won or self.n_submitted_guesses >= N_TRIES_ALLOWED
