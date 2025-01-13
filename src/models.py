import datetime as dt
import re

from pydantic import BaseModel, Field, field_validator, model_validator

SALARY_PATTERN = r"\d+"
LAST_VISITED_PATTERN = (
    r"(\d+)\s+(день|дня|дней|месяц|месяца|месяцев|год|года|лет)\s+назад"
)


class HabrCookies(BaseModel):
    remember_user_token: str


class HabrCareerUser(BaseModel):
    salary: int | None
    salary_unit: str | None = None
    availability: str
    qualification: str
    username: str = Field(alias="id")
    last_visited: str | dt.date | None = Field(validation_alias="lastVisited")

    _created_at: dt.date | None = None

    @field_validator("last_visited", mode="after")
    def set_last_activity(cls, last_visited: str | None) -> dt.date:
        error_message = "Неверный формат выражения"
        tz = dt.timezone(offset=dt.timedelta(hours=3))
        matched = re.match(LAST_VISITED_PATTERN, last_visited)
        today = dt.datetime.now(tz=tz).date()
        if not matched:
            if last_visited == "сегодня":
                return today
            raise ValueError(error_message)

        quantity = int(matched.group(1))
        unit = matched.group(2)

        if unit in ["день", "дня", "дней"]:
            return today - dt.timedelta(days=quantity)
        if unit in ["месяц", "месяца", "месяцев"]:
            year = today.year
            month = today.month - quantity
            while month < 1:
                month += 12
                year -= 1
            return today.replace(year=year, month=month, day=1)
        if unit in ["год", "года", "лет"]:
            return today.replace(year=today.year - quantity, month=1, day=1)
        raise ValueError(error_message)

    @field_validator("salary", mode="before")
    def preprocess_salary(cls, value: str) -> int | None:
        try:
            return re.findall(SALARY_PATTERN, value.replace(" ", ""))[0]
        except AttributeError:
            return None

    @model_validator(mode="before")
    def preprocess_salary_unit(cls, data: dict) -> dict:
        if data["salary"] is None:
            return data
        if data["salary"][-1].isdigit():
            return data
        data["salary_unit"] = data["salary"][-1]
        return data

    def dump_for_db(self) -> tuple:
        return (
            self.username,
            self.availability,
            self.qualification,
            self.salary,
            self.salary_unit,
            self.last_visited,
        )
