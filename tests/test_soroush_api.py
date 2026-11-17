"""Offline tests for the Soroush Plus client."""
import unittest
from unittest.mock import AsyncMock
from ertebat import soroush


class SoroushTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.bot = soroush.Ertebat("TEST_TOKEN")
        self.bot.request = AsyncMock(return_value=[{"update_id": 1}])

    async def test_import_and_alias(self):
        self.assertIs(soroush.Bot, soroush.Ertebat)
        self.assertEqual(self.bot.base_url, "https://api.splus.ir")

    async def test_get_me(self):
        await self.bot.get_me()
        self.bot.request.assert_awaited_with("getMe")

    async def test_send_message(self):
        await self.bot.send_message(123, "hello", reply_to_message_id=5)
        self.bot.request.assert_awaited_with("sendMessage", {
            "chat_id": 123, "text": "hello", "reply_to_message_id": 5
        })

    async def test_event_reply(self):
        event = soroush.Event(self.bot, {"message": {
            "message_id": 9, "text": "hi", "chat": {"id": 123}
        }})
        await event.reply("hello")
        self.bot.request.assert_awaited_with("sendMessage", {
            "chat_id": 123, "text": "hello", "reply_to_message_id": 9
        })

    async def test_command_dispatch(self):
        seen = []
        @self.bot.command("start")
        async def handler(bot, event):
            seen.append(event.text)
        await self.bot._dispatch({"message": {
            "message_id": 1, "text": "/start", "chat": {"id": 123}
        }})
        self.assertEqual(seen, ["/start"])

    async def test_callback_dispatch(self):
        seen = []
        @self.bot.callback()
        async def handler(bot, event):
            seen.append(event.button_id)
        await self.bot._dispatch({"callback_query": {"id": "q1", "data": "press"}})
        self.assertEqual(seen, ["press"])

    def test_empty_token(self):
        with self.assertRaises(ValueError):
            soroush.Ertebat(" ")


if __name__ == "__main__":
    unittest.main()
