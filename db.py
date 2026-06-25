import datetime
from database.connection import SessionLocal
from database.models import User, SleepRecord, Note
from errors_validators import db_error_handler
from sqlalchemy.exc import SQLAlchemyError
import os
import datetime
from database.connection import SessionLocal
from database.models import User, SleepRecord, Note
from errors_validators import db_error_handler
from sqlalchemy.exc import SQLAlchemyError
import os
import psycopg2
from dotenv import load_dotenv

def get_connection():
    """Возвращает соединение с PostgreSQL (используется для сырых SQL-запросов, например, при инициализации функций)"""
    load_dotenv()
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PW'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        return conn
    except Exception as e:
        print('❌ Ошибка соединения с базой:', e)
        return None

@db_error_handler
def add_user(user_id: int, name: str) -> None:
    """
    Добавляет пользователя в таблицу users, если его ещё нет.
    :param user_id: Telegram ID пользователя
    :param name: Имя пользователя (из Telegram)
    """
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            user = User(id=user_id, name=name)
            session.add(user)
            session.commit()
            print(f'User {user_id} добавлен')
        else:
            print(f'User {user_id} уже есть')
    except SQLAlchemyError as e:
        session.rollback()
        raise e
    finally:
        session.close()

@db_error_handler
def add_sleep_record(user_id: int, sleep_time: str, wake_time: str, sleep_quality: int) -> int:
    """
    Добавляет запись сна в таблицу sleep_records.
    :param user_id: Telegram ID пользователя
    :param sleep_time: время засыпания (строка, совместимая с PostgreSQL)
    :param wake_time: время пробуждения
    :param sleep_quality: оценка качества (1–5)
    :return: ID созданной записи
    """
    session = SessionLocal()
    try:
        record = SleepRecord(
            user_id=user_id,
            sleep_time=sleep_time,
            wake_time=wake_time,
            quality=sleep_quality
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        print(f'Запись {record.id} добавлена')
        return record.id
    except SQLAlchemyError as e:
        session.rollback()
        raise e
    finally:
        session.close()

@db_error_handler
def add_note(sleep_record_id: int, notes: str) -> int:
    """
    Добавляет заметку к существующей записи сна.
    :param sleep_record_id: ID записи в таблице sleep_records
    :param notes: текст заметки
    :return: ID созданной заметки
    """
    session = SessionLocal()
    try:
        note = Note(sleep_record_id=sleep_record_id, notes=notes)
        session.add(note)
        session.commit()
        session.refresh(note)
        print(f'Заметки для записи {sleep_record_id} добавлены')
        return note.id
    except SQLAlchemyError as e:
        session.rollback()
        raise e
    finally:
        session.close()

def add_full_record(user_id: int, name: str, sleep_time: str, wake_time: str, sleep_quality: int, notes: str) -> None:
    """
    Добавляет полную запись: пользователя (если нет), запись сна и заметку.
    Обёртка над add_user, add_sleep_record, add_note.
    """
    add_user(user_id, name)
    record_id = add_sleep_record(user_id, sleep_time, wake_time, sleep_quality)
    add_note(record_id, notes)

@db_error_handler
def extract_records_by_date(user_id: int, date: datetime.date) -> list[dict]:
    """
    Возвращает все записи сна пользователя за указанную дату.
    Использует SQL-функцию get_records_by_date.
    :param user_id: Telegram ID пользователя
    :param date: дата в формате datetime.date
    :return: список словарей с полями record_id, sleep_time, wake_time, duration, sleep_quality, notes
    """
    session = SessionLocal()
    try:
        result = session.execute(
            "SELECT * FROM get_records_by_date(:user_id, :date)",
            {"user_id": user_id, "date": date}
        ).fetchall()
        records_list = []
        for rec in result:
            records_list.append({
                'record_id': rec[0],
                'sleep_time': rec[1],
                'wake_time': rec[2],
                'duration': rec[3],
                'sleep_quality': rec[4],
                'notes': rec[5]
            })
        return records_list
    except SQLAlchemyError as e:
        raise e
    finally:
        session.close()

@db_error_handler
def calc_duration(record_id: int) -> str:
    """
    Вычисляет длительность сна по ID записи (использует SQL-функцию sleep_duration).
    Возвращает отформатированную строку 'X ч Y мин\n'.
    """
    session = SessionLocal()
    try:
        duration = session.execute(
            "SELECT sleep_duration(:record_id)",
            {"record_id": record_id}
        ).scalar()
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        return f'{hours} ч {minutes} мин\n'
    except SQLAlchemyError as e:
        raise e
    finally:
        session.close()

@db_error_handler
def show_full_stats(user_id: int):
    """
    Возвращает полную статистику сна для пользователя.
    Использует SQL-функцию show_statistics.
    :param user_id: Telegram ID пользователя
    :return: словарь с ключами: avg_duration, max_duration, min_duration, avg_quality,
             max_quality, min_quality, max_duration_date, min_duration_date, max_quality_date, min_quality_date
             или None, если записей нет.
    """
    session = SessionLocal()
    try:
        stats = session.execute(
            "SELECT * FROM show_statistics(:user_id)",
            {"user_id": user_id}
        ).fetchone()
        if stats is None:
            return None
        return {
            'avg_duration': stats[0],
            'max_duration': stats[1],
            'min_duration': stats[2],
            'avg_quality': stats[3],
            'max_quality': stats[4],
            'min_quality': stats[5],
            'max_duration_date': stats[6],
            'min_duration_date': stats[7],
            'max_quality_date': stats[8],
            'min_quality_date': stats[9],
        }
    except SQLAlchemyError as e:
        raise e
    finally:
        session.close()

@db_error_handler
def update_record(record_id: int, new_sleep_time: str, new_wake_time: str,
                  new_sleep_quality: int, new_notes: str) -> bool:
    """
    Обновляет существующую запись сна и заметку.
    :param record_id: ID записи
    :param new_sleep_time: новое время засыпания
    :param new_wake_time: новое время пробуждения
    :param new_sleep_quality: новая оценка качества
    :param new_notes: новый текст заметки (если заметки не было, создаётся новая)
    :return: True при успехе, False если запись не найдена
    """
    session = SessionLocal()
    try:
        record = session.query(SleepRecord).filter_by(id=record_id).first()
        if not record:
            return False
        record.sleep_time = new_sleep_time
        record.wake_time = new_wake_time
        record.quality = new_sleep_quality
        if record.note:
            record.note.notes = new_notes
        else:
            note = Note(sleep_record_id=record_id, notes=new_notes)
            session.add(note)
        session.commit()
        print(f'Запись {record_id} обновлена')
        return True
    except SQLAlchemyError as e:
        session.rollback()
        raise e
    finally:
        session.close()

@db_error_handler
def delete_record(record_id: int) -> bool:
    """
    Удаляет запись сна и связанную с ней заметку (каскадно).
    :param record_id: ID записи
    :return: True при успехе, False если запись не найдена
    """
    session = SessionLocal()
    try:
        record = session.query(SleepRecord).filter_by(id=record_id).first()
        if not record:
            return False
        session.delete(record)
        session.commit()
        print(f'Запись {record_id} удалена')
        return True
    except SQLAlchemyError as e:
        session.rollback()
        raise e
    finally:
        session.close()