"""Offline unit tests for the public IRubix API (no real bot token or network)."""
import asyncio
import unittest
from unittest.mock import AsyncMock

from irubix import IRubix, Event, RubikaAPIError


class FakeBot(IRubix):
    def __init__(self):
        super().__init__("TEST_TOKEN")
        self.calls = []

    async def request(self, method, input=None):
        self.calls.append((method, input))
        return {"status": "OK", "data": {"message_id": "MSG-1", "file_id": "FILE-1"}}


class PublicMethodsTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.bot = FakeBot()

    async def test_request(self):
        await self.bot.request("getMe")
        self.assertEqual(self.bot.calls[-1], ("getMe", None))

    async def test_get_me(self):
        await self.bot.get_me()
        self.assertEqual(self.bot.calls[-1][0], "getMe")

    async def test_get_chat(self):
        await self.bot.get_chat("CHAT")
        self.assertEqual(self.bot.calls[-1], ("getChat", {"chat_id": "CHAT"}))

    async def test_get_file(self):
        await self.bot.get_file("FILE")
        self.assertEqual(self.bot.calls[-1], ("getFile", {"file_id": "FILE"}))

    async def test_send_text_and_allowed_options(self):
        await self.bot.send_text("CHAT", "hello", disable_notification=True, ignored="x")
        self.assertEqual(self.bot.calls[-1], ("sendMessage", {
            "chat_id": "CHAT", "text": "hello", "disable_notification": True
        }))

    async def test_send_message_alias(self):
        await self.bot.send_message("CHAT", "hello")
        self.assertEqual(self.bot.calls[-1][0], "sendMessage")

    async def test_send_poll(self):
        await self.bot.send_poll("CHAT", "Question?", ["Yes", "No"])
        self.assertEqual(self.bot.calls[-1], ("sendPoll", {
            "chat_id": "CHAT", "question": "Question?", "options": ["Yes", "No"]
        }))

    async def test_send_poll_rejects_too_few_options(self):
        with self.assertRaises(ValueError):
            await self.bot.send_poll("CHAT", "Question?", ["Only one"])

    async def test_send_quiz_is_explicitly_unimplemented(self):
        with self.assertRaises(NotImplementedError):
            await self.bot.send_quiz()

    async def test_forward_message(self):
        await self.bot.forward_message("FROM", "MSG", "TO", True)
        self.assertEqual(self.bot.calls[-1][0], "forwardMessage")
        self.assertTrue(self.bot.calls[-1][1]["disable_notification"])

    async def test_edit_message_text(self):
        await self.bot.edit_message_text("CHAT", "MSG", "new")
        self.assertEqual(self.bot.calls[-1][0], "editMessageText")

    async def test_delete_message(self):
        await self.bot.delete_message("CHAT", "MSG")
        self.assertEqual(self.bot.calls[-1], ("deleteMessage", {
            "chat_id": "CHAT", "message_id": "MSG"
        }))

    async def test_ban_and_unban(self):
        await self.bot.ban_chat_member("CHAT", "USER")
        self.assertEqual(self.bot.calls[-1][0], "banChatMember")
        await self.bot.unban_chat_member("CHAT", "USER")
        self.assertEqual(self.bot.calls[-1][0], "unbanChatMember")

    async def test_send_file_flow(self):
        self.bot.request = AsyncMock(side_effect=[
            {"status": "OK", "data": {"upload_url": "https://upload.invalid"}},
            {"status": "OK", "data": {"message_id": "MSG-2"}},
        ])
        self.bot._upload_sync = lambda *args: "FILE-1"
        await self.bot.send_file("CHAT", b"demo", text="caption", file_name="demo.txt")
        self.assertEqual(self.bot.request.await_args_list[0].args[0], "requestSendFile")
        self.assertEqual(self.bot.request.await_args_list[1].args[0], "sendFile")

    async def test_command_handler(self):
        seen = []
        @self.bot.command("start")
        async def handler(bot, event):
            seen.append(event.text)
        await self.bot._dispatch({"type": "NewMessage", "message": {
            "chat_id": "CHAT", "message_id": "M1", "text": "/start"
        }})
        self.assertEqual(seen, ["/start"])

    async def test_message_handler_and_filter(self):
        seen = []
        @self.bot.message(lambda event: event.text == "hello")
        async def handler(bot, event):
            seen.append(event.text)
        await self.bot._dispatch({"message": {"chat_id": "C", "text": "ignore"}})
        await self.bot._dispatch({"message": {"chat_id": "C", "text": "hello"}})
        self.assertEqual(seen, ["hello"])

    async def test_callback_handler(self):
        seen = []
        @self.bot.callback()
        async def handler(bot, event):
            seen.append(event.button_id)
        await self.bot._dispatch({"button_id": "BTN-1"})
        self.assertEqual(seen, ["BTN-1"])

    async def test_event_reply(self):
        event = Event(self.bot, {"message": {
            "chat_id": "CHAT", "message_id": "M1", "text": "hi"
        }})
        await event.reply("hello")
        self.assertEqual(self.bot.calls[-1][1]["reply_to_message_id"], "M1")

    async def test_event_reply_without_chat_raises(self):
        event = Event(self.bot, {})
        with self.assertRaises(RubikaAPIError):
            await event.reply("hello")

    async def test_start_validates_arguments(self):
        with self.assertRaises(ValueError):
            await self.bot.start(poll_interval=0.01)
        with self.assertRaises(ValueError):
            await self.bot.start(limit=101)

    async def test_stop(self):
        self.bot.stop()
        self.assertFalse(self.bot._running)

    def test_run_returns_coroutine_inside_event_loop(self):
        result = self.bot.run()
        self.assertTrue(asyncio.iscoroutine(result))
        result.close()

    def test_empty_token_rejected(self):
        with self.assertRaises(ValueError):
            IRubix("  ")


if __name__ == "__main__":
    unittest.main(verbosity=2)
