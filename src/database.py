import asyncpg
from asyncpg import UniqueViolationError
from asyncpg.pool import PoolConnectionProxy
from loguru import logger
from pydantic import PostgresDsn

from src.models import HabrCareerUser


class Database:
    def __init__(self, dsn: PostgresDsn) -> None:
        self.dsn = dsn.unicode_string()
        self.pool = None

    async def connect(self) -> None:
        self.pool = await asyncpg.create_pool(dsn=self.dsn)
        logger.debug("Created database pool")

    async def create_tables(self) -> None:
        async with self.pool.acquire() as connection:
            await self._create_habr_career_user_table(connection)
            await self._create_users_to_check_table(connection)
        logger.debug("Created database tables")

    async def _create_habr_career_user_table(
        self, connection: PoolConnectionProxy
    ) -> None:
        query = """
        CREATE TABLE IF NOT EXISTS habr_career_users (
            id serial PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            last_visited DATE NOT NULL,
            status varchar(100) NOT NULL,
            salary integer,
            salary_unit VARCHAR(2),
            qualification VARCHAR(255) NOT NULL,
            created_at TIMESTAMP default now()
        )
        """
        await connection.execute(query)
        logger.debug("Created habr_career_users table")
        index = """
        CREATE UNIQUE INDEX IF NOT EXISTS unique_user_fields_nullable
        ON habr_career_users (
            COALESCE(username, username),
            COALESCE(status, status),
            COALESCE(qualification, qualification),
            COALESCE(salary, 0),
            COALESCE(salary_unit, 'NULL'),
            COALESCE(last_visited, last_visited)
        );
        """
        await connection.execute(index)
        logger.debug("Created habr_career_users unique index")

    async def _create_users_to_check_table(
        self, connection: PoolConnectionProxy
    ) -> None:
        query = """
        CREATE TABLE IF NOT EXISTS users_to_check (
        username VARCHAR(255) PRIMARY KEY
        )
        """
        await connection.execute(query)
        logger.debug("Created users_to_check table")

    async def insert_user(self, user: HabrCareerUser) -> None:
        query = (
            "INSERT INTO habr_career_users (username, status, qualification,"
            "salary, salary_unit, last_visited) "
            "VALUES ($1, $2, $3, $4, $5, $6)"
        )

        async with self.pool.acquire() as connection:
            try:
                await connection.execute(query, *user.dump_for_db())
                logger.info(f"Inserted user {user}")
            except UniqueViolationError:
                logger.warning(f"Row {user} already exists")

    async def insert_user_to_check(self, username: str) -> None:
        query = "INSERT INTO users_to_check (username) VALUES ($1)"
        async with self.pool.acquire() as connection:
            await connection.execute(query, username)

    async def get_users_to_check(self) -> list[str]:
        query = "SELECT * FROM users_to_check"
        async with self.pool.acquire() as connection:
            return [res[0] for res in await connection.fetch(query)]

    async def get_min_user_last_visited(self, username: str) -> None:
        query = (
            "SELECT min(last_visited) FROM habr_career_users "
            "WHERE username = $1 GROUP BY username "
        )
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, username)
