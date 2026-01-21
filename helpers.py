import datetime
from database import extract_records_by_date


def format_date_for_output(date_input) -> str | None:
    """Конвертация даты для сообщений"""
    if not date_input:
        return None
    if isinstance(date_input, str):
        try:
            date_input = datetime.datetime.fromisoformat(date_input).date()
        except ValueError:
            return None

    return date_input.strftime('%d-%m-%Y')



def load_records_by_date(user_id: int, search_date: datetime.date) -> list[dict] | str:
    """"
    Функция выгружает данные записи по дате
    :param: user_id: id пользователя
    :param: text: str: ввод пользователя

    :return records_found: list: полные данные о записи или 'Wrong date format' если ошибка
    :Raises ValueError если дата не проходит проверку формата
    """
    data = extract_records_by_date(user_id, search_date)
    if not data:
        return []
    return data

def convert_duration(duration_sec: datetime.timedelta) -> dict:
    """Конвертация длительности сна в часы:минуты"""
    total_minutes = duration_sec.total_seconds() // 60
    hours = int(total_minutes // 60)
    minutes = int(total_minutes % 60)
    return {'hrs': hours, 'min': minutes}



