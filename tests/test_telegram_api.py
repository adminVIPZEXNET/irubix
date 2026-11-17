import unittest
from unittest.mock import AsyncMock
from ertebat import telegram

class TelegramTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.bot = telegram.Ertebat("TEST_TOKEN")
        self.bot.request = AsyncMock(return_value={"message_id": 10})

    async def test_import_alias_and_base_url(self):
        self.assertIs(telegram.Bot, telegram.Ertebat)
        self.assertEqual(self.bot.base_url, "https://api.telegram.org")

    async def test_empty_token(self):
        with self.assertRaises(ValueError): telegram.Ertebat(" ")

    async def test_get_me(self):
        await self.bot.get_me()
        self.bot.request.assert_awaited_with("getMe")

    async def test_send_message(self):
        await self.bot.send_message(123, "hello", parse_mode="HTML")
        self.bot.request.assert_awaited_with("sendMessage", {"chat_id":123,"text":"hello","parse_mode":"HTML"})

    async def test_event_reply(self):
        event = telegram.Event(self.bot, {"message":{"message_id":9,"text":"hi","chat":{"id":123}}})
        await event.reply("hello")
        self.bot.request.assert_awaited_with("sendMessage", {"chat_id":123,"text":"hello","reply_parameters":{"message_id":9}})

    async def test_command_dispatch(self):
        seen=[]
        @self.bot.command("start")
        async def handler(bot,event): seen.append(event.text)
        await self.bot._dispatch({"message":{"message_id":1,"text":"/start@sample_bot","chat":{"id":123}}})
        self.assertEqual(seen, ["/start@sample_bot"])

    async def test_callback_dispatch(self):
        seen=[]
        @self.bot.callback()
        async def handler(bot,event): seen.append(event.button_id)
        await self.bot._dispatch({"callback_query":{"id":"q1","data":"pressed","message":{"chat":{"id":123},"message_id":7}}})
        self.assertEqual(seen, ["pressed"])

    async def test_update_validation(self):
        with self.assertRaises(ValueError): await self.bot.get_updates(limit=0)

if __name__ == "__main__": unittest.main()
