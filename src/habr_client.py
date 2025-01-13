import json
import re

from httpx import AsyncClient
from loguru import logger

from src.models import HabrCareerUser, HabrCookies

USER_PATTERN = re.compile(r'data-ssr-state="true">({.*?})</script>', re.DOTALL)
SALARY_PATTERN = r"\d+"


def get_user_data(html: str) -> dict:
    matched = USER_PATTERN.search(html)
    json_data = matched.group(1)
    if json_data:
        return json.loads(json_data)
    raise ValueError


def parse_salary(salary: str) -> int | None:
    try:
        return re.findall(SALARY_PATTERN, salary.replace(" ", ""))[0]
    except AttributeError:
        return None


class HabrClient:
    def __init__(self, cookies: HabrCookies) -> None:
        self._token_url = "https://career.habr.com/integrations/oauth/token"  # noqa: S105
        self.client = AsyncClient(cookies=cookies.model_dump(by_alias=True))
        self.url = "https://career.habr.com"

    async def get_user_data(self, username: str) -> HabrCareerUser:
        page_data = await self.get_page_data(username)
        user = self.parse_page_data(page_data)
        logger.info(f"Success fetched {username}")
        return user

    async def get_page_data(self, username: str) -> str:
        url = f"{self.url}/{username}"
        page = await self.client.get(url)
        return page.text

    @staticmethod
    def parse_page_data(page: str) -> HabrCareerUser:
        data = get_user_data(page)
        user = data["user"]
        salary = parse_salary(user["salary"])
        data["user"]["salary"] = salary
        return HabrCareerUser(**data["user"])
