import datetime as dt

import pytest
from freezegun import freeze_time

from src.models import HabrCareerUser


@pytest.fixture
def default_user() -> dict:
    return {
        "salary": "50 000 Р",
        "availability": "Ищу работу",
        "qualification": "Старший",
        "id": "testUsername",
        "lastVisited": "сегодня",
    }


last_activity_params = (
    ("сегодня", "2025-01-13"),
    ("1 день назад", "2025-01-12"),
    ("2 дня назад", "2025-01-11"),
    ("3 дня назад", "2025-01-10"),
    ("5 дней назад", "2025-01-08"),
    ("6 дней назад", "2025-01-07"),
    ("15 дней назад", "2024-12-29"),
    ("31 день назад", "2024-12-13"),
    ("1 месяц назад", "2024-12-01"),
    ("2 месяца назад", "2024-11-01"),
    ("3 месяца назад", "2024-10-01"),
    ("5 месяцев назад", "2024-08-01"),
    ("6 месяцев назад", "2024-07-01"),
    ("8 месяцев назад", "2024-05-01"),
    ("11 месяцев назад", "2024-02-01"),
    ("1 год назад", "2024-01-01"),
    ("2 года назад", "2023-01-01"),
    ("3 года назад", "2022-01-01"),
    ("5 лет назад", "2020-01-01"),
    ("6 лет назад", "2019-01-01"),
)

salary_params = [(None, None), ("От 200 000 ₽", 200_000)]


@pytest.mark.parametrize(("last_visited", "result"), last_activity_params)
@freeze_time("2025-01-13")
def test_set_last_activity_days(
    last_visited: str, result: str, default_user: dict
):
    default_user["lastVisited"] = last_visited
    user_model = HabrCareerUser.model_validate(default_user)
    assert user_model.last_visited == dt.date.fromisoformat(result)


@pytest.mark.parametrize(("salary", "result"), salary_params)
def test_parse_salary(salary: str, result: int | None, default_user: dict):
    default_user["salary"] = salary
    user_model = HabrCareerUser.model_validate(default_user)
    assert user_model.salary == result


@pytest.mark.parametrize(
    ("salary", "salary_unit"),
    [(None, None), ("От 200 000 ₽", "₽"), ("От 15 000 $", "$")],
)
def test_parse_salary_unit(
    salary: str | None, salary_unit: str | None, default_user: dict
):
    default_user["salary"] = salary
    user_model = HabrCareerUser.model_validate(default_user)
    assert user_model.salary_unit == salary_unit
