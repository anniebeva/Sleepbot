from database.models import Base
from database.connection import engine
from db import get_connection   

def init_db():
    Base.metadata.create_all(engine)

    conn = get_connection()
    if not conn:
        print("❌ Не удалось подключиться к БД для создания функций")
        return
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE OR REPLACE FUNCTION get_records_by_date(p_user_id BIGINT, p_date DATE)
                RETURNS TABLE(record_id INTEGER, sleep_time TIMESTAMP, wake_time TIMESTAMP, 
                              duration INTERVAL, sleep_quality INTEGER, notes TEXT) AS $$
                BEGIN
                    RETURN QUERY
                    SELECT sr.id, sr.sleep_time, sr.wake_time, 
                           (sr.wake_time - sr.sleep_time) AS duration, sr.quality, n.notes
                    FROM sleep_records sr
                    LEFT JOIN notes n ON sr.id = n.sleep_record_id
                    WHERE sr.user_id = p_user_id AND DATE(sr.sleep_time) = p_date
                    ORDER BY sr.sleep_time;
                END;
                $$ LANGUAGE plpgsql;
            """)
            cur.execute("""
                CREATE OR REPLACE FUNCTION sleep_duration(p_record_id INTEGER)
                RETURNS INTERVAL AS $$
                DECLARE dur INTERVAL;
                BEGIN
                    SELECT wake_time - sleep_time INTO dur FROM sleep_records WHERE id = p_record_id;
                    RETURN dur;
                END;
                $$ LANGUAGE plpgsql;
            """)
            cur.execute("""
                CREATE OR REPLACE FUNCTION show_statistics(p_user_id BIGINT)
                RETURNS TABLE(avg_duration INTERVAL, max_duration INTERVAL, min_duration INTERVAL,
                              avg_quality NUMERIC, max_quality INTEGER, min_quality INTEGER,
                              max_duration_date DATE, min_duration_date DATE, 
                              max_quality_date DATE, min_quality_date DATE) AS $$
                BEGIN
                    RETURN QUERY
                    SELECT AVG(wake_time - sleep_time), MAX(wake_time - sleep_time), MIN(wake_time - sleep_time),
                           AVG(quality)::NUMERIC(3,1), MAX(quality), MIN(quality),
                           (SELECT DATE(sleep_time) FROM sleep_records WHERE user_id = p_user_id AND wake_time - sleep_time = MAX(wake_time - sleep_time) LIMIT 1),
                           (SELECT DATE(sleep_time) FROM sleep_records WHERE user_id = p_user_id AND wake_time - sleep_time = MIN(wake_time - sleep_time) LIMIT 1),
                           (SELECT DATE(sleep_time) FROM sleep_records WHERE user_id = p_user_id AND quality = MAX(quality) LIMIT 1),
                           (SELECT DATE(sleep_time) FROM sleep_records WHERE user_id = p_user_id AND quality = MIN(quality) LIMIT 1)
                    FROM sleep_records WHERE user_id = p_user_id;
                END;
                $$ LANGUAGE plpgsql;
            """)
        conn.commit()
        print("✅ База данных инициализирована (таблицы и функции созданы/обновлены)")
    except Exception as e:
        print(f"❌ Ошибка при создании функций: {e}")
        conn.rollback()
    finally:
        conn.close()
