from enum import Enum


class NameMatch(Enum):
    EXACT_MATCH = "exact"
    PARTIAL_MATCH = "partial"
    NO_MATCH = "none"


QUESTIONS_PER_DAY = 5
IMAGE_RESOLUTIONS = [8, 15, 25, 50, 198]

with open("bot_token.txt") as f:
    BOT_TOKEN = f.readlines()[0]

with open("encryption_key.txt") as f:
    # Unsafely stored in a plain text file, but we don't really care
    # as this is just to prevent cheating
    ENCRYPTION_KEY = f.readlines()[0]
