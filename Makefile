up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f --tail=200

test:
	PYTHONPATH=. pytest -q

health:
	curl -fsS http://127.0.0.1:8501/_stcore/health && echo
