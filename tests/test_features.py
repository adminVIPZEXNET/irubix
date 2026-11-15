"""Offline tests for platform-neutral IRubix utilities."""
import asyncio
import tempfile
import unittest
from pathlib import Path

from irubix import (
    AIAdapter, BotStats, CloudStorageAdapter, CommandPermissions,
    ConversationManager, FileManager, MessageBuilder, MiddlewareManager,
    PluginManager, RateLimiter, WebhookAdapter, UniversalEventRouter, KeyboardBuilder,\n    SessionManager, UniversalClient,
)


class FeatureTests(unittest.TestCase):
    def test_stats(self):
        stats = BotStats()
        stats.record_message("rubika", 2)
        stats.record_error("network")
        data = stats.snapshot()
        self.assertEqual(data["total_messages"], 2)
        self.assertEqual(data["total_errors"], 1)

    def test_permissions(self):
        permissions = CommandPermissions()
        permissions.set_role("1", "admin")
        self.assertTrue(permissions.allows("1", "ban"))
        permissions.grant("2", "read")
        self.assertTrue(permissions.allows("2", "read"))
        self.assertFalse(permissions.allows("2", "ban"))

    def test_file_manager_prevents_path_traversal(self):
        with tempfile.TemporaryDirectory() as root:
            files = FileManager(root)
            files.save("data/test.txt", "hello")
            self.assertEqual(files.read("data/test.txt", text=True), "hello")
            with self.assertRaises(ValueError):
                files.save("../escape.txt", "no")

    def test_rate_limiter(self):
        limiter = RateLimiter(1, capacity=1)
        self.assertTrue(limiter.try_acquire("user"))
        self.assertFalse(limiter.try_acquire("user"))

    def test_conversation(self):
        async def scenario():
            manager = ConversationManager()
            manager.begin("chat", data={"step": 1})
            self.assertTrue(manager.active("chat"))
            await manager.feed("chat", "answer")
            self.assertEqual(await manager.wait("chat", timeout=0.1), "answer")
            manager.end("chat")
            self.assertFalse(manager.active("chat"))
        asyncio.run(scenario())

    def test_middleware_order(self):
        async def scenario():
            middleware = MiddlewareManager()
            calls = []
            async def first(ctx, next_call):
                calls.append("before")
                await next_call()
                calls.append("after")
            async def handler(ctx):
                calls.append("handler")
            middleware.add(first)
            await middleware.execute(handler, {})
            self.assertEqual(calls, ["before", "handler", "after"])
        asyncio.run(scenario())

    def test_adapters(self):
        async def scenario():
            ai = AIAdapter(lambda prompt: "answer:" + prompt)
            self.assertEqual(await ai.ask("hi"), "answer:hi")
            cloud = CloudStorageAdapter(
                lambda name, data: (name, len(data)),
                lambda name: name.encode(),
            )
            self.assertEqual(await cloud.upload("x", b"abc"), ("x", 3))
            self.assertEqual(await cloud.download("x"), b"x")
        asyncio.run(scenario())

    def test_webhook_secret(self):
        async def scenario():
            webhook = WebhookAdapter(lambda payload: payload["id"], "secret")
            self.assertEqual(await webhook.handle({"id": 3}, "secret"), 3)
            with self.assertRaises(PermissionError):
                await webhook.handle({}, "wrong")
        asyncio.run(scenario())

    def test_message_builder_uses_generic_client(self):
        class Client:
            async def send_text(self, chat_id, text, **kwargs):
                return (chat_id, text, kwargs)
        async def scenario():
            builder = MessageBuilder("hello").reply_to_message("m1")
            result = await builder.send(Client(), "chat")
            self.assertEqual(result[0][0:2], ("chat", "hello"))
            self.assertEqual(result[0][2]["reply_to_message_id"], "m1")
        asyncio.run(scenario())

    def test_keyboard_builder(self):
        keyboard = KeyboardBuilder(inline=True).button("OK", callback_data="ok").new_row().button("Docs", url="https://example.com")
        built = keyboard.build()
        self.assertTrue(built["inline"])
        self.assertEqual(len(built["rows"]), 2)

    def test_event_router(self):
        async def scenario():
            router = UniversalEventRouter()
            seen = []
            @router.on("message")
            async def handler(event):
                seen.append(event.text)
            class Event:
                type = "message"
                text = "hello"
            await router.dispatch(Event())
            self.assertEqual(seen, ["hello"])
        asyncio.run(scenario())

    def test_plugin_manager_rejects_missing_file(self):
        with tempfile.TemporaryDirectory() as root:
            manager = PluginManager()
            with self.assertRaises(FileNotFoundError):
                manager.load(Path(root) / "missing.py")


    def test_persistent_sessions(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "sessions.json"
            sessions = SessionManager(path)
            sessions.create("user-1", {"step": "name"})
            sessions.set("user-1", "name", "Ada")
            restored = SessionManager(path)
            self.assertEqual(restored.get("user-1", "name"), "Ada")
            self.assertTrue(restored.delete("user-1"))
            self.assertIsNone(SessionManager(path).get("user-1"))

    def test_universal_client_facade(self):
        class Client:
            async def send_message(self, chat_id, text, **kwargs):
                return {"chat_id": chat_id, "text": text}
        async def scenario():
            client = UniversalClient(telegram=Client())
            result = await client.send_text("telegram", 123, "hello")
            self.assertEqual(result, {"chat_id": 123, "text": "hello"})
            self.assertEqual(client.platforms(), ("telegram",))
        asyncio.run(scenario())

    def test_message_builder_sends_caption_once(self):
        class Client:
            def __init__(self):
                self.calls = []
            async def send_file(self, chat_id, file, **kwargs):
                self.calls.append((chat_id, file, kwargs))
                return "sent"
        async def scenario():
            client = Client()
            builder = MessageBuilder("caption").add_file("photo.jpg", file_type="Image")
            result = await builder.send(client, "chat")
            self.assertEqual(result, ["sent"])
            self.assertEqual(len(client.calls), 1)
            self.assertEqual(client.calls[0][2]["text"], "caption")
        asyncio.run(scenario())

if __name__ == "__main__":
    unittest.main()
