import datetime
from dotenv import load_dotenv
from errors_validators import db_error_handler
import os
import psycopg2

#Note: Tables, indexes, and functions were created within Pgadmin Postgres Database

def get_connection():
    """Подключение к Базе Данных"""
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
    except psycopg2.OperationalError as e:
        print('❌ Ошибка соединения с базой:', e)
        return None
    except Exception as e:
        print('❌ Неожиданная ошибка:', e)
        return None

@db_error_handler
def add_user(user_id: int, name: str) -> None:
    """"
    Добавляет запись сна в базу данных

    :return: Добавляет запись в таблицу users в БД sleepbot.db если юзера еще нет
    :raises Exception: Если произошла ошибка при работе с БД
    """
    query_check = 'SELECT id FROM users WHERE id = %s'
    query_insert = 'INSERT INTO users (id, name) VALUES (%s, %s)'

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query_check, (user_id,))
            if cursor.fetchone():
                print(f'User {user_id} уже есть')
            else:
                cursor.execute(query_insert, (user_id, name))
                conn.commit()
                print(f'User {user_id} добавлен')

@db_error_handler
def add_sleep_record(user_id: int, sleep_time: str, wake_time: str, sleep_quality: int) -> int|None:
    """"
    Добавляет запись в таблицу sleep_records в БД sleepbot.db

    :return: ID записи сна (int) или None при ошибке
    :raises Exception: Если произошла ошибка при работе с БД
    """

    insert_data_query = ("""INSERT INTO sleep_records (user_id, sleep_time, wake_time, quality)
                           VALUES (%s, %s, %s, %s)
                           Returning id""")
    sleep_r = (user_id, sleep_time, wake_time, sleep_quality)

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(insert_data_query, sleep_r)
            record_id = cursor.fetchone()[0]
            conn.commit()
            print(f'Запись {record_id} добавлена')
            return record_id

@db_error_handler
def add_note(sleep_record_id: int, notes: str) -> None:
    """"
    Добавляет запись в таблицу notes в БД sleepbot.db

    :return: ID заметки для дальнейшего использованиия
    :raises Exception: Если произошла ошибка при работе с БД
    """
    insert_data_query = ("""INSERT INTO notes (sleep_record_id, notes)
                         VALUES (%s, %s)
                         Returning id""")
    notes_r = (sleep_record_id, notes)

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(insert_data_query, notes_r)
            note_id = cursor.fetchone()[0]
            conn.commit()
            print(f'Заметки для записи {sleep_record_id} добавлены')
            return note_id


def add_full_record(user_id: int, name: str, sleep_time: str, wake_time: str, sleep_quality: int, notes: str) -> None:

    """"
    Общая функция для добавлений всех данных о сне в таблицы users, sleep_records, и notes в БД sleepbot.db
    :return: Добавляет запись в соответствующие таблицы в БД sleepbot.db
    """

    add_user(user_id, name)
    record_id = add_sleep_record(user_id, sleep_time, wake_time, sleep_quality)
    add_note(record_id, notes)

@db_error_handler
def extract_records_by_date(user_id: int, date: datetime.date) -> list[dict] | None:
    """
    Выводит данные о всех данных сна для конкретного пользователя в дату

    :returns list[Dict]: Информация
    :raises Exception: Если произошла ошибка при работе с БД
    """
    select_query = "SELECT * FROM get_records_by_date(%s, %s)"

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(select_query, (user_id, date))
            all_records = cursor.fetchall()

            records_list = []
            for rec in all_records:
                records_list.append({
                    'record_id': rec[0],
                    'sleep_time': rec[1],
                    'wake_time': rec[2],
                    'duration': rec[3],
                    'sleep_quality': rec[4],
                    'notes': rec[5]
                })

            return records_list

@db_error_handler
def calc_duration(record_id: int) -> str|None:
    """
    Подсчет и форматирование длительности сна

    :returns str: датf в формате {hours} ч {minutes} мин
    """
    query = "SELECT * FROM sleep_duration(%s)"

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (record_id,))
            duration = cursor.fetchone()[0]

            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60

            return f'{hours} ч {minutes} мин\n'

@db_error_handler
def show_full_stats(user_id: int):
    """Вывод статистики по user_id"""

    query = "SELECT * FROM show_statistics(%s)"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (user_id, ))
            all_stats = cursor.fetchone()

            if all_stats is None:
                return None

            print (all_stats)

            return {
                'avg_duration': all_stats[0],
                'max_duration': all_stats[1],
                'max_duration_date': all_stats[6],
                'min_duration_date': all_stats[7],
                'min_duration': all_stats[2],
                'avg_quality': all_stats[3],
                'max_quality': all_stats[4],
                'max_quality_date': all_stats[8],
                'min_quality': all_stats[5],
                'min_quality_date': all_stats[9],
            }

@db_error_handler
def update_record(record_id: int, new_sleep_time: str,
                  new_wake_time: str, new_sleep_quality: int, new_notes: str) -> bool:
    """
    Изменяет данные записи в таблицах sleep_records и notes в ДБ sleepbor.db

    :print: 'Запись {record_id} обновлена' при успешном выполнении функции
    :return bool: True/False обновлена ли запись успешно
    :raises Exception: Если произошла ошибка при работе с БД
    """
    update_sleep_query = '''
            UPDATE sleep_records
            SET sleep_time = %s, wake_time = %s, quality = %s
            WHERE id = %s
            '''
    update_notes_query = '''
            UPDATE notes
            SET notes = %s
            WHERE sleep_record_id = %s
            '''

    update_sleep_r = (new_sleep_time, new_wake_time, new_sleep_quality, record_id)
    update_notes_r = (new_notes, record_id)

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(update_sleep_query, update_sleep_r)
            cursor.execute(update_notes_query, update_notes_r)
            conn.commit()
            print(f'Запись {record_id} обновлена')
            return True

@db_error_handler
def delete_record(record_id: int) -> bool:
    """
    Удаляет запись и все данные о ней из таблиц sleep_records, notes из ДБ sleepbot.db

    :return bool: True/False индикатор удаления записи
    :print: 'Запись {id} удалена' если функция сработала

    :raises Exception: Если произошла ошибка при работе с БД
    """

    delete_notes_query = '''
            DELETE FROM notes
            WHERE sleep_record_id = %s
            '''

    delete_sleep_query = '''
            DELETE FROM sleep_records
            WHERE id = %s
            '''

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(delete_notes_query, (record_id,))
            cursor.execute(delete_sleep_query, (record_id, ))
            conn.commit()
            print(f'Запись {record_id} обновлена')
            return True

