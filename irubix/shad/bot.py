"""Async client for the Shad Bot API (unofficially documented)."""
from __future__ import annotations

import asyncio
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable


class ShadAPIError(RuntimeError):
    """Raised when Shad returns an API or transport error."""


class Event:
    """Normalized incoming Shad update."""

    def __init__(self, bot: "IRubix", raw: dict[str, Any]):
        self.bot = bot
        self.raw = raw
        self.update = raw
        self.message = raw.get("message") or raw.get("edited_message") or raw
        self.chat = self.message.get("chat") or {}
        self.chat_id = self.message.get("chat_id") or self.chat.get("chat_id") or self.chat.get("id")
        self.message_id = self.message.get("message_id") or self.message.get("id")
        self.text = self.message.get("text") or self.message.get("body") or ""
        self.sender = self.message.get("from") or self.message.get("sender") or {}
        self.sender_id = self.sender.get("user_id") or self.sender.get("id")
        self.type = "message" if self.message else "unknown"

    async def reply(self, text: str, **kwargs):
        if self.chat_id is None:
            raise ShadAPIError("Chat ID was not found in this update.")
        if self.message_id is not None:
            kwargs.setdefault("reply_to_message_id", self.message_id)
        return await self.bot.send_message(self.chat_id, text, **kwargs)


class IRubix:
    """Shad bot client using the Shad v3 bot endpoint.

    The endpoint and method names are based on the publicly available,
    unofficial shad-api implementation; Shad does not provide public
    official documentation for this interface.
    """
    API_URL = "https://shadmessengerg2b1.iranlms.ir/v3"
    __version__ = "0.6.0"

    def __init__(self, token: str, *, timeout: float = 40, base_url: str | None = None):
        if not isinstance(token, str) or not token.strip():
            raise ValueError("Shad bot token must not be empty.")
        self.token = token.strip()
        self.base_url = (base_url or self.API_URL).rstrip("/")
        self.timeout = timeout
        self._handlers: list[tuple[str, Any, Callable]] = []
        self._running = False
        self._offset_id = None

    def _request_sync(self, method: str, payload: dict | None = None):
        if not method or "/" in method:
            raise ValueError("Invalid API method name.")
        url = f"{self.base_url}/{urllib.parse.quote(self.token, safe='')}/{method}"
        data = json.dumps(payload or {}, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            url, data=data,
            headers={"Content-Type": "application/json; charset=utf-8",
                     "Accept": "application/json", "User-Agent": f"IRubix-Shad/{self.__version__}"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")
            raise ShadAPIError(f"HTTP {exc.code}: {detail}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise ShadAPIError(f"Connection error: {exc}") from exc
        try:
            result = json.loads(body)
        except json.JSONDecodeError as exc:
            raise ShadAPIError("Shad returned invalid JSON.") from exc
        if not isinstance(result, dict):
            raise ShadAPIError("Unexpected Shad API response.")
        if result.get("status") != "OK":
            raise ShadAPIError(str(result.get("message") or result.get("error") or result))
        return result.get("data", result)

    async def request(self, method: str, payload: dict | None = None):
        """Call a Shad bot API method."""
        return await asyncio.to_thread(self._request_sync, method, payload)

    async def get_me(self):
        return await self.request("getMe", {})

    async def get_updates(self, *, limit: int = 10, offset_id: str | None = None):
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100.")
        payload = {"limit": limit}
        if offset_id is not None:
            payload["offset_id"] = offset_id
        return await self.request("getUpdates", payload)

    async def send_message(self, chat_id, text: str, **kwargs):
        payload = {"chat_id": chat_id, "text": text}
        for key in ("chat_keypad", "chat_keypad_type", "inline_keypad",
                    "disable_notification", "reply_to_message_id"):
            if kwargs.get(key) is not None:
                value = kwargs[key]
                if key in ("chat_keypad", "inline_keypad") and hasattr(value, "dict"):
                    value = value.dict()
                payload[key] = value
        return await self.request("sendMessage", payload)

    async def send_poll(self, chat_id, question: str, options: list, **kwargs):
        payload = {"chat_id": chat_id, "question": question, "options": options}
        payload.update({k: v for k, v in kwargs.items() if v is not None})
        return await self.request("sendPoll", payload)

    async def send_location(self, chat_id, latitude: float, longitude: float, **kwargs):
        payload = {"chat_id": chat_id, "latitude": latitude, "longitude": longitude}
        payload.update({k: v for k, v in kwargs.items() if v is not None})
        return await self.request("sendLocation", payload)

    async def send_sticker(self, chat_id, sticker_id, **kwargs):
        payload = {"chat_id": chat_id, "sticker_id": sticker_id}
        payload.update({k: v for k, v in kwargs.items() if v is not None})
        return await self.request("sendSticker", payload)

    async def send_contact(self, chat_id, first_name, last_name, phone_number, **kwargs):
        payload = {"chat_id": chat_id, "first_name": first_name,
                   "last_name": last_name, "phone_number": phone_number}
        payload.update({k: v for k, v in kwargs.items() if v is not None})
        return await self.request("sendContact", payload)

    async def forward_message(self, from_chat_id, message_id, to_chat_id, **kwargs):
        payload = {"from_chat_id": from_chat_id, "message_id": message_id,
                   "to_chat_id": to_chat_id}
        payload.update({k: v for k, v in kwargs.items() if v is not None})
        return await self.request("forwardMessage", payload)

    async def edit_message_text(self, chat_id, message_id, text: str):
        return await self.request("editMessageText", {
            "chat_id": chat_id, "message_id": message_id, "text": text
        })

    async def delete_message(self, chat_id, message_id):
        return await self.request("deleteMessage", {
            "chat_id": chat_id, "message_id": message_id
        })

    async def edit_message_keypad(self, chat_id, message_id, inline_keypad):
        if hasattr(inline_keypad, "dict"):
            inline_keypad = inline_keypad.dict()
        return await self.request("editMessageKeypad", {
            "chat_id": chat_id, "message_id": message_id, "inline_keypad": inline_keypad
        })

    async def edit_chat_keypad(self, chat_id, chat_keypad):
        if hasattr(chat_keypad, "dict"):
            chat_keypad = chat_keypad.dict()
        return await self.request("editChatKeypad", {
            "chat_id": chat_id, "chat_keypad_type": "New", "chat_keypad": chat_keypad
        })

    async def remove_chat_keypad(self, chat_id):
        return await self.request("editChatKeypad", {
            "chat_id": chat_id, "chat_keypad_type": "Remove"
        })

    async def send_file(self, chat_id, file_id, **kwargs):
        payload = {"chat_id": chat_id, "file_id": file_id}
        payload.update({k: v for k, v in kwargs.items() if v is not None})
        return await self.request("sendFile", payload)

    async def request_send_file(self, file_type: str):
        return await self.request("requestSendFile", {"type": file_type})

    async def get_file(self, file_id):
        return await self.request("getFile", {"file_id": file_id})

    async def get_chat(self, chat_id):
        return await self.request("getChat", {"chat_id": chat_id})

    async def set_commands(self, bot_commands):
        commands = [c.dict() if hasattr(c, "dict") else c for c in bot_commands]
        return await self.request("setCommands", {"bot_commands": commands})

    async def update_bot_endpoints(self, url: str, endpoint_type: str):
        return await self.request("updateBotEndpoints", {"url": url, "type": endpoint_type})

    def command(self, names):
        commands = [names] if isinstance(names, str) else list(names)
        commands = [str(name).lstrip("/") for name in commands]
        def decorator(function):
            self._handlers.append(("command", commands, function))
            return function
        return decorator

    def message(self, flt=None):
        def decorator(function):
            self._handlers.append(("message", flt, function))
            return function
        return decorator

    async def _dispatch(self, raw: dict):
        event = Event(self, raw)
        for kind, value, handler in tuple(self._handlers):
            if kind == "command":
                command = event.text.strip().split(maxsplit=1)[0].split("@", 1)[0].lstrip("/") if event.text.strip() else ""
                if not event.text.startswith("/") or command not in value:
                    continue
            elif kind == "message":
                if not event.message:
                    continue
                if callable(value) and not value(event):
                    continue
            try:
                result = handler(self, event)
                if hasattr(result, "__await__"):
                    await result
            except Exception as exc:
                print(f"[IRubix:Shad] Handler error: {exc}")

    async def start(self, *, limit: int = 10, retry_delay: float = 2):
        self._running = True
        print("[IRubix:Shad] Bot started.")
        while self._running:
            try:
                result = await self.get_updates(limit=limit, offset_id=self._offset_id)
                if isinstance(result, dict):
                    updates = result.get("updates") or result.get("messages") or result.get("items") or []
                    self._offset_id = result.get("next_offset_id") or result.get("offset_id") or self._offset_id
                else:
                    updates = result or []
                if isinstance(updates, dict):
                    updates = list(updates.values())
                for update in updates:
                    if not isinstance(update, dict):
                        continue
                    await self._dispatch(update)
                    self._offset_id = (update.get("update_id") or update.get("message_id")
                                       or update.get("message", {}).get("message_id")
                                       or self._offset_id)
                if not updates:
                    await asyncio.sleep(0.5)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                print(f"[IRubix:Shad] Polling error: {exc}")
                await asyncio.sleep(retry_delay)
        print("[IRubix:Shad] Bot stopped.")

    def stop(self):
        self._running = False

    def run(self, *, limit: int = 10, retry_delay: float = 2):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            try:
                asyncio.run(self.start(limit=limit, retry_delay=retry_delay))
            except KeyboardInterrupt:
                self.stop()
            return None
        return self.start(limit=limit, retry_delay=retry_delay)


Bot = IRubix
