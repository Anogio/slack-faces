install:
	pip install -r requirements.txt

start_debug:
	flask --app api.app  --debug run

start:
	gunicorn -w 5 -b 0.0.0.0:5002 api.app:app

start_daemon_server:
	gunicorn -w 5 -b 0.0.0.0:5002 --daemon api.app:app

format:
	black .