install:
	pip install -r requirements.txt

start_debug:
	flask --app api.app  --debug run

start:
	gunicorn -w 5 api.app:app -b 127.0.0.1:5000

format:
	black .