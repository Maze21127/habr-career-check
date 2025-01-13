import asyncio
import json
import os

import anyio
from loguru import logger
from pydantic import PostgresDsn

from src.database import Database
from src.habr_client import HabrClient
from src.models import HabrCookies


async def main() -> None:
    async with await anyio.open_file("habr_cookies.json") as f:
        content = await f.read()
        cookies = HabrCookies(**json.loads(content))
    db = Database(PostgresDsn(os.getenv("DB_DSN")))
    await db.connect()
    await db.create_tables()

    users = await db.get_users_to_check()

    client = HabrClient(cookies)
    for username in users:
        user = await client.get_user_data(username)
        min_visited = await db.get_min_user_last_visited(username)
        if min_visited and min_visited[0][0] > user.last_visited:
            logger.warning(f"User {username} logged earlier")
            continue
        await db.insert_user(user)
        await db.insert_user(user)


if __name__ == "__main__":
    asyncio.run(main())
