"""Offline tests for the Shad Bot API client."""
import unittest
from unittest.mock import AsyncMock
from irubix import shad


class ShadTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.bot = shad.IRubix("TEST_TOKEN")
        self.bot.request = AsyncMock(return_value={"message_id": 10})

    async def test_import_alias_and_url(self):
        self.assertIs(shad.Bot, shad.IRubix)
        self.assertEqual(self.bot.base_url, "https://shadmessengerg2b1.iranlms.ir/v3")

    async def test_get_me(self):
        await self.bot.get_me()
        self.bot.request.assert_awaited_with("getMe", {})

    async def test_send_message(self):
        await self.bot.send_message("chat1", "hello", reply_to_message_id="m1")
        self.bot.request.assert_awaited_with("sendMessage", {
            "chat_id": "chat1", "text": "hello", "reply_to_message_id": "m1"
        })

    async def test_event_reply(self):
        event = shad.Event(self.bot, {"message": {
            "message_id": "m1", "text": "hi", "chat_id": "chat1"
        }})
        await event.reply("hello")
        self.bot.request.assert_awaited_with("sendMessage", {
            "chat_id": "chat1", "text": "hello", "reply_to_message_id": "m1"
        })

    async def test_command_dispatch(self):
        seen = []
        @self.bot.command("start")
        async def handler(bot, event):
            seen.append(event.text)
        await self.bot._dispatch({"message": {
            "message_id": "m1", "text": "/start", "chat_id": "chat1"
        }})
        self.assertEqual(seen, ["/start"])

    async def test_empty_token(self):
        with self.assertRaises(ValueError):
            shad.IRubix(" ")


if __name__ == "__main__":
    unittest.main()
