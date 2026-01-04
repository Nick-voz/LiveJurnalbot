# Live Journal Bot

A Telegram bot for personal journaling and tracking metrics. Users can create custom scenarios with parameters and record values over time, with optional reminders to keep them on track.

## Features

- **Scenarios**: Create custom scenarios (e.g., "Health", "Work Productivity", "Mood Tracking") to organize your metrics.
- **Parameters**: Add parameters to each scenario (e.g., "Weight", "Hours Slept", "Mood Score") with optional default values.
- **Records**: Easily record values for parameters with timestamps in Moscow timezone.
- **Data Export**: Ability to get data in .csv, .excel, .pdf formats. (Not yet implemented)
- **Reminders**: Set up reminder strategies to prompt you to log data regularly. (Not yet implemented)
- **User-Friendly Interface**: Interactive menus and conversation flows via Telegram buttons and messages.

## Technology Stack

- **Language**: Python 3.12+
- **Bot Framework**: python-telegram-bot
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Alembic
- **Containerization**: Docker & Docker Compose
- **Package Management**: uv
- **Code Quality**: Black, isort, pylint, pyright

## Usage

1. Start a chat with your bot at [https://t.me/LivJurnalbot](https://t.me/LivJurnalbot) and send `/start`.
2. Use the menu to:
   - Create new scenarios
   - View and manage existing scenarios
   - Record values for parameters
   - Set up reminders

Available commands:

- `/start` or `/menu`: Open main menu
