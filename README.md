# 🍔 Burger Alert

A weekly burger ordering app for coordinating Thursday lunch orders from [Big Daddy Burger Bar](https://www.facebook.com/BigDaddyBurgerBar). Built with Flask, SQLite, and a custom dark/light UI.

## Features

- **Order form** with live preview, character counter, and countdown timer
- **Dine-in / takeout** selection with conditional transport and LIPÓTI Bakery options
- **Today's orders** view with dine-in and takeout sections, delete support
- **Car distribution** — automatic passenger assignment with seat grid visualization
- **Dark (charcoal) / light (parchment) theme** toggle, persisted in localStorage
- **Mobile-first** bottom tab bar for small screens, sticky desktop header
- **Menu modal** with zoomable Big Daddy menu images
- **Order history resets daily** at midnight (via `cleaner.py`)

## Quick Start

### Docker (recommended)

```bash
cp .env_template .env
# edit .env with your values
docker compose up -d
```

The app runs behind Caddy on ports 80/443. Edit `caddy-conf/Caddyfile` for your domain and TLS certs.

### Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env_template .env
flask --app app run --debug
```

## Environment Variables

| Variable | Description |
|---|---|
| `APP_VERSION` | Version string shown in the header |
| `NO_TIME_CONSTRAINT` | Set to `true` or `1` to allow ordering outside Thursday 1:00–13:00 |

## Project Structure

```
├── app.py                  # Flask app, routes, DB models, car distribution logic
├── cleaner.py              # Cron script to wipe orders nightly
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── caddy-conf/Caddyfile
├── static/
│   ├── css/main.css        # Full custom stylesheet (dark/light themes)
│   ├── css/fonts/          # HomeVideo font
│   └── images/             # Menu images, favicons
└── templates/
    ├── base.html           # Layout: header, nav, theme toggle, mobile tabs, menu modal
    ├── index.html          # Order form with countdown, preview, collapsible sections
    ├── today_orders.html   # Order cards with tags and delete
    ├── car_distribution.html # Car cards with seat grid
    ├── confirmation.html   # Animated success page
    └── failed.html         # Error page
```

## Ordering Rules

- Ordering opens on **Thursdays** between configured hours (default 1:00–13:00)
- Closes at **11:05** (countdown shown on order page)
- Dine-in capacity is limited by available drivers × 5 seats
- Overflow dine-in orders get bumped to takeout
- LIPÓTI Bakery passengers get priority seating with LIPÓTI drivers
