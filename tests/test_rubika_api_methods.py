import unittest
from unittest.mock import AsyncMock

from irubix import Rubika, BotModel, Chat, File, Message, Update


class RubikaAPIMethodTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.bot = Rubika("test-token")
        self.bot.request = AsyncMock(return_value={"status": "OK", "data": {}})

    async def test_get_updates(self):
        await self.bot.get_updates("offset-1", limit=20)
        self.bot.request.assert_awaited_once_with(
            "getUpdates", {"limit": 20, "offset_id": "offset-1"}
        )

    async def test_send_location(self):
        await self.bot.send_location("chat-1", 35.7, 51.4, disable_notification=True)
        self.bot.request.assert_awaited_once_with("sendLocation", {
            "chat_id": "chat-1", "latitude": "35.7", "longitude": "51.4",
            "disable_notification": True,
        })

    async def test_send_contact(self):
        await self.bot.send_contact("chat-1", "Ada", "+100", last_name="Lovelace")
        self.bot.request.assert_awaited_once_with("sendContact", {
            "chat_id": "chat-1", "first_name": "Ada",
            "last_name": "Lovelace", "phone_number": "+100",
        })

    async def test_edit_inline_keypad(self):
        keypad = {"rows": [{"buttons": []}]}
        await self.bot.edit_inline_keypad("chat-1", "message-1", keypad)
        self.bot.request.assert_awaited_once_with("editInlineKeypad", {
            "chat_id": "chat-1", "message_id": "message-1",
            "inline_keypad": keypad,
        })

    async def test_edit_chat_keypad_remove(self):
        await self.bot.edit_chat_keypad("chat-1", chat_keypad_type="Remove")
        self.bot.request.assert_awaited_once_with("editChatKeypad", {
            "chat_id": "chat-1", "chat_keypad_type": "Remove",
        })

    async def test_set_commands(self):
        commands = [{"command": "start", "description": "Start"}]
        await self.bot.set_commands(commands)
        self.bot.request.assert_awaited_once_with("setCommands", {
            "bot_commands": commands,
        })

    async def test_webhook_requires_https(self):
        with self.assertRaises(ValueError):
            await self.bot.update_bot_endpoints("http://example.com/hook", "ReceiveUpdate")

    async def test_webhook(self):
        await self.bot.update_bot_endpoints(
            "https://example.com/hook", "ReceiveInlineMessage"
        )
        self.bot.request.assert_awaited_once_with("updateBotEndpoints", {
            "url": "https://example.com/hook", "type": "ReceiveInlineMessage",
        })

    async def test_request_send_file(self):
        await self.bot.request_send_file("Image")
        self.bot.request.assert_awaited_once_with(
            "requestSendFile", {"type": "Image"}
        )

    async def test_send_file_id(self):
        await self.bot.send_file_id("chat-1", "file-1", text="caption")
        self.bot.request.assert_awaited_once_with("sendFile", {
            "chat_id": "chat-1", "file_id": "file-1", "text": "caption",
        })

    async def test_process_update_webhook_envelope(self):
        seen = []

        @self.bot.command("start")
        async def start(bot, event):
            seen.append((event.chat_id, event.text, event.command))

        await self.bot.process_update({"update": {
            "type": "NewMessage",
            "chat_id": "chat-1",
            "new_message": {"message_id": "m1", "text": "/start", "sender_id": "u1"},
        }})
        self.assertEqual(seen, [("chat-1", "/start", "start")])

    async def test_process_inline_message_webhook_envelope(self):
        seen = []

        @self.bot.callback()
        async def callback(bot, event):
            seen.append((event.chat_id, event.message_id, event.button_id))

        await self.bot.process_webhook({"inline_message": {
            "sender_id": "u1", "text": "Clicked",
            "aux_data": {"button_id": "btn-1"},
            "message_id": "m2", "chat_id": "chat-2",
        }})
        self.assertEqual(seen, [("chat-2", "m2", "btn-1")])

    async def test_invalid_values(self):
        with self.assertRaises(ValueError):
            await self.bot.get_updates(limit=0)
        with self.assertRaises(ValueError):
            await self.bot.request_send_file("Unknown")
        with self.assertRaises(ValueError):
            await self.bot.edit_chat_keypad("chat-1", chat_keypad_type="Invalid")


class RubikaModelTests(unittest.TestCase):
    def test_models_are_exported(self):
        self.assertEqual(File.from_dict({"file_id": "f1"}).file_id, "f1")
        self.assertEqual(Chat.from_dict({"chat_id": "c1"}).chat_id, "c1")
        self.assertEqual(Message.from_dict({"text": "hello"}).text, "hello")
        self.assertEqual(Update.from_dict({"type": "NewMessage"}).type, "NewMessage")
        self.assertTrue(hasattr(BotModel, "from_dict"))


if __name__ == "__main__":
    unittest.main()
