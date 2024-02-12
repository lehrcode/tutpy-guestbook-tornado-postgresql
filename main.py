import asyncio
import logging

from tornado.httpserver import HTTPServer
from tornado.options import define, options, parse_command_line
from tornado.web import Application

define("port", default=8080, help="port to listen on")


async def main():
    app = Application()
    server = HTTPServer(app)
    logging.info('Start listening on port %d', options.port)
    server.listen(options.port)
    shutdown_event = asyncio.Event()
    await shutdown_event.wait()


if __name__ == '__main__':
    parse_command_line()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('Shutting down')
