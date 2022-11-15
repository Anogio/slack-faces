install:
	pip install -r requirements.txt

start_debug:
	flask --app api.app  --debug run

start:
	gunicorn -w 5 api.app:app -b 0.0.0.0:5002

format:
	black .