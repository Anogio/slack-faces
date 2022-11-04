# Facedle

A daily face-guessing game based on Slack profile pictures.

## Setup
### Backend
**Install the requirements:**
```
pip install -r back/requirements.txt
```

**Add the Slack app token:**
- Download the file on [Google drive](https://drive.google.com/file/d/18OO-hPJeJODNj_YA1SELJ2x8ry3s8E6H/view?usp=sharing) 
(restricted to Doctrine)
- Put it in the `back` folder

**NB**: The app can work on any Slack workspace, provided with 
the proper token. All you need is an authentication token for an app
with the `users:read` scope, that you will put in a `bot_token.txt`
file.

### Frontend
**Install the project:** 
```
yarn install
```

## Run the app locally
- Run the backend: `cd back && make start` (use `make start_debug` for hot reload)
- Serve the frontend `cd front && yarn serve`

The server will be run on port 5000 and the front on port 8080.