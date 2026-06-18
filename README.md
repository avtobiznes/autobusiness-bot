# Telegram Bot - Applications Collector

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Docker

```bash
docker build -t bot .
docker run --env-file .env bot
```

## Environment Variables

| Variable             | Description               |
| -------------------- | ------------------------- |
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather |
| `TELEGRAM_CHAT_ID`   | Target group chat ID      |
| `PROXY_URL`          | Proxy URL (optional)      |

## Data Storage

Applications stored in `applications.db` (SQLite) with fields:

- `user_id`, `username`, `brand_model`, `phone_username`, `created_at`

## Bot Flow

1. `/start` → ask for brand/model
2. User enters brand/model → ask for phone/username
3. User enters phone/username → application sent to group + saved to DB
4. User receives confirmation message
