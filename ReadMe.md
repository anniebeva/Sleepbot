# 💤 SleepBot  

**SleepBot** is a Telegram bot that helps users track their sleep:  
record sleep and wake times, sleep quality, notes, and view or manage past records.

The project is built with **Python**, **Telegram Bot API**, and **PostgreSQL**.

---

## 🚀 Features

- Add sleep records:
  - sleep time
  - wake time
  - sleep quality
  - notes
- View sleep records by date
- Edit existing records
- Delete records
- Basic sleep statistics
- Multi-step user interaction via Telegram bot handlers

---

## 🛠 Tech Stack

- **Python 3.10+**
- **pyTelegramBotAPI (telebot)** – Telegram Bot API wrapper
- **PostgreSQL** – production‑ready relational database
- **SQLAlchemy ORM** – database modelling and session management
- **psycopg2-binary** – PostgreSQL adapter for Python
- **python-dotenv** – environment variable management
- **Flask** – web server for webhooks (deployment)
- **SQL functions** – defined in Python and created automatically at startup

---

## ⚙️ Setup & Installation

### 1️⃣ Clone the repository

```
git clone https://github.com/your-username/sleepbot.git
cd sleepbot
```

2️⃣ Create and activate virtual environment
```
python -m venv venv
```

3️⃣ Install dependencies

```
pip install -r requirements.txt
```

## 🤖 Telegram Bot Setup

- Create a bot via @BotFather

- Copy your bot token

- Set it as an environment variable:
    export TELEGRAM_API_KEY=your_token_here
    Or use a .env file if preferred.

## 🗄 Database Setup (IMPORTANT)

> **Important:** The required tables and SQL functions are **automatically created** when the bot starts for the first time. You don't need to run any manual SQL scripts.

---

### Option 1: Local PostgreSQL (for development)

1. Install and start PostgreSQL on your machine.

2. Create a database and a user (if they don't exist). Example in `psql`:

   ```sql
   CREATE DATABASE sleepbot;
   CREATE USER sleepbot WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE sleepbot TO sleepbot;
   ```
3. Create a .env file in the project root:

```
TELEGRAM_API_KEY=your_bot_token
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sleepbot
DB_USER=sleepbot
DB_PW=your_password
USE_WEBHOOK=false   # use polling for local development
```

### Option 2: Cloud PostgreSQL (for production)
Use a cloud provider like Render, Supabase, or Neon. Copy the connection string and split it into separate environment variables.

Example for Render PostgreSQL:

```
DB_HOST=dpg-xxxxx.oregon-postgres.render.com
DB_PORT=5432
DB_NAME=sleepbot_db
DB_USER=sleepbot_db_user
DB_PW=your_password
```

## ▶️ Run the Bot

```
python run.py
```

## 🧠 Architectural Notes
- Handlers are registered via side-effect imports in run.py
- Each handler module registers commands using @bot.message_handler decorators
- User state between steps is stored in an in-memory user_sessions dictionary
- Database logic is isolated from Telegram handlers (clean separation)
- ORM layer uses SQLAlchemy for all database operations
- SQL functions (e.g., get_records_by_date, show_statistics) are created automatically at startup
- Two deployment modes:
  - Polling – used for local development 
  - Webhooks – used for production (prevents bot from sleeping on Render)


## Possible Improvements (Planned)
- Add more tests: helper functions, mock tests
- Code Structure: reduce handler duplication, improve readability and connectivity
- Fix decorators, errors validation for dates
- UI / UX: improve bot functions, error messaging, input options