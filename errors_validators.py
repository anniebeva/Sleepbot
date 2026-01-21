import datetime

class InvalidFormatError(ValueError):
    pass

class OutOfRangeError(ValueError):
    pass


def validate_nums_in_range(value: str, start: int, end: int) -> int:
    """"
        Функция для валидации чисел в определенном рендже

        :returns: число в формате int или None при error
        :raises ValueError если число вне рамок
        :raises Typerror если ввод не число
        """
    try:
        num = int(value)
    except ValueError:
        raise InvalidFormatError('Неверный формат числа.')

    if not (start <= num <= end):
        raise OutOfRangeError(f'Число должно быть между {start} и {end}.')

    return num

def parse_user_date(date_input: str) -> datetime.date|None:
    """Конвертация даты из соообщения в вормат datetime.date"""
    try:
        date = datetime.datetime.strptime(date_input, '%d-%m-%Y').date()
        if date > datetime.date.today():
            return None

    except ValueError:
        return None


    return date

def parse_user_time(time_input: str) -> datetime.time|None:
    """Конвертация времени из сообщения в формат datetime.time"""
    try:
        return datetime.datetime.strptime(time_input, '%H:%M').time()
    except ValueError:
        return None

#DB exceptions

class DatabaseError(Exception):
    pass

def db_error_handler(func):
    """Wrapper для ошибок Базы данных. Ловит ошибки"""
    def wrapper(*args, **kwargs):
        try: return func(*args, **kwargs)
        except Exception as e:
            raise DatabaseError(f'Ошибка БД в {func.__name__}: {e}')

    return wrapper




