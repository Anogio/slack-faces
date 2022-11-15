SLACK_CLIENT_ID = "20725405907.4331386221344"

QUESTIONS_PER_DAY = 5
N_TRIES_ALLOWED = 5
IMAGE_RESOLUTIONS = [8, 15, 25, 50, 198]
assert len(IMAGE_RESOLUTIONS) == N_TRIES_ALLOWED

with open("secrets/bot_token.txt") as f:
    BOT_TOKEN = f.readlines()[0]

with open("secrets/encryption_key.txt") as f:
    # Unsafely stored in a plain text file, but we don't really care
    # as this is just to prevent cheating
    ENCRYPTION_KEY = f.readlines()[0]

with open("secrets/slack_client_secret.txt") as f:
    SLACK_CLIENT_SECRET = f.readlines()[0]
