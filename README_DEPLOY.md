# HERMES AI AGENT — deploy-ready package

## Что внутри
- Функциональный MVP HERMES AI AGENT.
- Экспериментальная тёмная тема GUREEV VECTOR · HERMES Dark Concept v0.1.
- Dockerfile, docker-compose.yml, healthcheck, скрипты deploy/update/backup.
- Локальная парольная защита через переменную окружения `APP_PASSWORD_CHANGE_ME`.

## Быстрый запуск
```bash
cp .env.example .env
# задайте APP_PASSWORD_CHANGE_ME и LLM_API_KEY
bash scripts/deploy.sh
```

## Обновление
```bash
bash scripts/update.sh
```

## Резервная копия
```bash
bash scripts/backup.sh
```

## Примечания
- Постоянные данные хранятся в `./data`.
- Без заполнения `.env` приложение не должно считаться готовым к продуктивному вводу в эксплуатацию.
- Пароль можно задать в открытом виде или как bcrypt-хеш.
