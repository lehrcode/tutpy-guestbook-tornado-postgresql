from datetime import datetime
from http import HTTPStatus

import asyncpg
from tornado.web import RequestHandler, HTTPError

MAX_ENTRIES_PER_PAGE = 5


class Entry:
    def __init__(self, id: int, name: str, email: str, message: str, posted: datetime):
        self.id = id
        self.name = name
        self.email = email
        self.message = message
        self.posted = posted


class EntryRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.__pool = pool

    def __from_record(self, rec: asyncpg.Record) -> Entry:
        return Entry(rec['id'], rec['name'], rec['email'], rec['message'], rec['posted'])

    async def add_entry(self, name: str, email: str, message: str):
        await self.__pool.execute("""
                                  INSERT INTO "entry" ("name", "email", "message")
                                  VALUES ($1, $2, $3)
                                  """,
                                  name, email, message)

    async def count_entries(self) -> int:
        return (await self.__pool.fetchrow('SELECT count(*) AS total_entries FROM "entry"'))['total_entries']

    async def get_entries(self, page: int) -> list[Entry]:
        entries = await self.__pool.fetch("""
                                          SELECT "id", "name", "email", "message", "posted"
                                          FROM "entry"
                                          ORDER BY posted DESC
                                          LIMIT $1 OFFSET $2
                                          """,
                                          MAX_ENTRIES_PER_PAGE, (page - 1) * MAX_ENTRIES_PER_PAGE)
        return [self.__from_record(x) for x in entries]


class GuestbookHandler(RequestHandler):
    def initialize(self, repo: EntryRepository):
        self.__repo = repo

    async def post(self):
        name = self.get_body_argument('name')
        email = self.get_body_argument('email')
        message = self.get_body_argument('message')
        await self.__repo.add_entry(name, email, message)
        self.redirect('/guestbook')

    async def get(self):
        page = int(self.get_query_argument('page', '1'))
        if page < 1:
            raise HTTPError(HTTPStatus.BAD_REQUEST, 'invalid page argument')
        total_entries = await self.__repo.count_entries()
        entries = await self.__repo.get_entries(page)
        await self.render('guestbook.html',
                          entries=entries,
                          page=page,
                          total_entries=total_entries,
                          MAX_ENTRIES_PER_PAGE=MAX_ENTRIES_PER_PAGE)
