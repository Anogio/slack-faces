serve_local_app:
	source venv/bin/activate && cd back && make install && make start_daemon_server && cd ../front && yarn install && make serve_prod_app