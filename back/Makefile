install:
	pip install -r requirements.txt

start_debug:
	flask --app app  --debug run

start:
	gunicorn -w 5 app:app -b 127.0.0.1:5000

format:
	black .