import tempfile
import unittest
from pathlib import Path

from ertebat._bot_api import BotAPIMethods, encode_request_payload


class FakeBot(BotAPIMethods):
    def __init__(self):
        self.calls = []

    async def request(self, method, payload=None):
        self.calls.append((method, payload))
        return {"method": method, "payload": payload}


class BotAPIDispatchTests(unittest.IsolatedAsyncioTestCase):
    async def test_snake_case_endpoint(self):
        bot = FakeBot()
        await bot.send_media_group(chat_id=123, media=[{"type": "photo"}])
        self.assertEqual(bot.calls[-1], (
            "sendMediaGroup", {"chat_id": 123, "media": [{"type": "photo"}]}
        ))

    async def test_camel_case_endpoint(self):
        bot = FakeBot()
        await bot.sendWidget(chat_id=123, widget={"html": "<p>Hi</p>"})
        self.assertEqual(bot.calls[-1][0], "sendWidget")

    async def test_common_positional_arguments(self):
        bot = FakeBot()
        await bot.send_video(123, "video-file-id", caption="Demo")
        self.assertEqual(bot.calls[-1], (
            "sendVideo", {"chat_id": 123, "video": "video-file-id", "caption": "Demo"}
        ))

    async def test_exact_method_passthrough(self):
        bot = FakeBot()
        await bot.call_api("sendSharedWidget", chat_id=123, widget_id="w1")
        self.assertEqual(bot.calls[-1], (
            "sendSharedWidget", {"chat_id": 123, "widget_id": "w1"}
        ))

    async def test_rejects_duplicate_positional_and_keyword_values(self):
        bot = FakeBot()
        with self.assertRaises(TypeError):
            await bot.send_video(123, chat_id=456, video="clip")

    async def test_file_path_uses_multipart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "photo.jpg"
            path.write_bytes(b"ERTEBAT-FILE-CONTENT")
            body, content_type = encode_request_payload({
                "chat_id": 123, "photo": path, "caption": "hello"
            })
        self.assertTrue(content_type.startswith("multipart/form-data; boundary="))
        self.assertIn(b'filename="photo.jpg"', body)
        self.assertIn(b"ERTEBAT-FILE-CONTENT", body)
        self.assertIn(b'name="caption"', body)

    async def test_json_payload_without_files(self):
        body, content_type = encode_request_payload({"chat_id": 123, "text": "hello"})
        self.assertEqual(content_type, "application/json")
        self.assertIn(b'"text": "hello"', body)


if __name__ == "__main__":
    unittest.main()
