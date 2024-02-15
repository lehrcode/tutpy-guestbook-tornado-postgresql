import asyncio
import logging

import asyncpg
from tornado.httpserver import HTTPServer
from tornado.options import define, options, parse_command_line
from tornado.web import Application, RedirectHandler

from guestbook import EntryRepository, GuestbookHandler, GuestbookAPIHandler

define("port", default=8080, help="port to listen on")
define("pgurl", default='postgres://postgres:@localhost:5432/postgres', help="PostgreSQL URL")


async def main():
    pool = await asyncpg.create_pool(options.pgurl)
    repo = EntryRepository(pool)
    app = Application([
        (r"/", RedirectHandler, {'url': '/guestbook'}),
        (r"/guestbook", GuestbookHandler, {'repo': repo}),
        (r"/api/v1/entries", GuestbookAPIHandler, {'repo': repo})
    ], static_path='assets', template_path='templates')
    server = HTTPServer(app)
    logging.info('Start listening on port %d', options.port)
    server.listen(options.port)
    shutdown_event = asyncio.Event()
    await shutdown_event.wait()
    await pool.close()


if __name__ == '__main__':
    parse_command_line()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('Shutting down')
