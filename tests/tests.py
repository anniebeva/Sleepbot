import pytest
from errors_validators import parse_user_date
import datetime

#To be updated, more tests to be added

def test_valid_date():
    result = parse_user_date('31-08-2025')
    assert isinstance(result, datetime.date)
    assert result == datetime.date(2025, 8, 31)

def test_invalid_date_format():
    result = parse_user_date('2025-08-31')
    assert result == None

def test_invalid_value():
    result = parse_user_date('99-99-9999')
    assert result == None

#
# def test_load_records_by_date(user_id: int, text: str):
#     assert 1, 22-08-2024 == '22-08-2024'



