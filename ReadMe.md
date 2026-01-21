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
- **pyTelegramBotAPI (telebot)**
- **PostgreSQL**
- **psycopg2**
- **SQL functions and indexes** (*created directly in PostgreSQL)


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

⚠️ Note on PostgreSQL 
Tables, indexes, and SQL functions were created directly inside PostgreSQL
(using pgAdmin), not via Python migrations or SQL files.

This project assumes that the database schema already exists.

### Required database objects
1. Tables:
- users
- sleep_records
- notes

2. PostgreSQL functions (examples):
- get_records_by_date(user_id, date)

Example usage of PostgreSQL function in Python

```
select_query = 'SELECT * FROM get_records_by_date(%s, %s)'
cursor.execute(select_query, (user_id, date))
```

## 📌 Database Connection

Configure your PostgreSQL credentials in .env

Connect via:

 ```
conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PW'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
```

## ▶️ Run the Bot

```
python run.py
```

## 🧠 Architectural Notes
Handlers are registered via side-effect imports in run.py

Each handler module registers commands using decorators

User state between steps is stored in an in-memory user_sessions dictionary

Database logic is isolated from Telegram handlers

### Limitations
- Database schema is not created automatically
- SQL functions are not stored in this repository
- No migrations or schema versioning
- In-memory session storage (lost on restart)

## Possible Improvements (Planned)
- Add more tests: helper functions, mock tests
- Database & Architecture: Store PostgreSQL functions in .sql files inside the repository
- Code Structure: reduce handler duplication, improve readability and connectivity
- Fix decorators, errors validation for dates
- UI / UX: improve bot functions, error messaging, input options