import json
from http import HTTPStatus
from unittest.mock import AsyncMock

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from guestbook import GuestbookAPIHandler

repo = AsyncMock()
repo.count_entries.return_value = 5


class TestGuestbookAPIHandler(AsyncHTTPTestCase):
    def get_app(self):
        return Application([(r"/api/v1/entries", GuestbookAPIHandler, {"repo": repo})])

    def test_post_bad_request(self):
        response = self.fetch(
            '/api/v1/entries',
            method='POST',
            body='{"message": "Bad Request"}')
        self.assertEqual(response.code, HTTPStatus.BAD_REQUEST)

    def test_post_created(self):
        response = self.fetch(
            '/api/v1/entries',
            method='POST',
            body=json.dumps({
                "name": "Test",
                "email": "test@example.org",
                "message": "Good"
            }))
        self.assertEqual(response.code, HTTPStatus.CREATED)

    def test_get_ok(self):
        response = self.fetch('/api/v1/entries', method='GET')
        self.assertEqual(response.code, HTTPStatus.OK)
        self.assertTrue(response.headers["Content-Type"].startswith("application/json"))
