"""Independent Rubika Bot API client using only Python standard library."""
from __future__ import annotations

import asyncio
import json
import mimetypes
import os
import secrets
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable


class RubikaAPIError(RuntimeError):
    """Raised when Rubika Bot API returns an error."""


class Event:
    """Normalized incoming update passed to registered handlers."""
    def __init__(self, bot: "IRubix", raw: dict[str, Any]):
        self.bot = bot
        self.raw = raw
        self.type = raw.get("type", "")
        self.update = raw
        msg = raw.get("message") or raw.get("new_message") or raw.get("updated_message") or {}
        if not isinstance(msg, dict):
            msg = {}
        self.message = msg
        self.chat_id = (raw.get("chat_id") or msg.get("chat_id") or
                        (msg.get("chat", {}) or {}).get("chat_id"))
        self.message_id = msg.get("message_id") or raw.get("message_id")
        self.text = msg.get("text") or raw.get("text") or ""
        self.sender_id = (msg.get("sender_id") or msg.get("author_object_guid") or
                          raw.get("sender_id") or raw.get("user_id"))
        self.button_id = raw.get("button_id") or raw.get("data")
        self.update_type = self.type

    async def reply(self, text: str, **kwargs: Any):
        if not self.chat_id:
            raise RubikaAPIError("شناسه چت در این رویداد پیدا نشد.")
        kwargs.setdefault("reply_to_message_id", self.message_id)
        return await self.bot.send_text(self.chat_id, text, **kwargs)


class IRubix:
    """Rubika bot client. No third-party runtime dependencies are required."""
    API_URL = "https://botapi.rubika.ir/v3"

    def __init__(self, token: str, *, timeout: float = 30, base_url: str | None = None):
        if not isinstance(token, str) or not token.strip():
            raise ValueError("توکن ربات نباید خالی باشد.")
        self.token = token.strip()
        self.base_url = (base_url or self.API_URL).rstrip("/") + "/" + self.token
        self.timeout = timeout
        self._handlers: list[tuple[str, Any, Callable]] = []
        self._running = False

    def _request_sync(self, method: str, payload: dict | None = None):
        url = self.base_url + "/" + method
        body = json.dumps(payload or {}, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers={
            "Content-Type": "application/json", "User-Agent": "IRubix/0.2.0"
        }, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")
            raise RubikaAPIError(f"HTTP {exc.code}: {detail}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise RubikaAPIError(f"خطای ارتباط با روبیکا: {exc}") from exc
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RubikaAPIError("پاسخ نامعتبر از سرور روبیکا") from exc
        if isinstance(data, dict) and data.get("status") not in (None, "OK"):
            raise RubikaAPIError(data.get("dev_message") or data.get("status"))
        return data

    async def request(self, method: str, input: dict | None = None):
        """Call a Rubika Bot API method asynchronously."""
        return await asyncio.to_thread(self._request_sync, method, input)

    async def send_text(self, chat_id: str, text: str, **kwargs):
        payload = {"chat_id": chat_id, "text": text}
        allowed = ("metadata", "chat_keypad", "inline_keypad", "reply_to_message_id",
                   "disable_notification", "chat_keypad_type")
        payload.update({k: v for k, v in kwargs.items() if k in allowed and v is not None})
        return await self.request("sendMessage", payload)

    async def send_message(self, chat_id: str, text: str, **kwargs):
        return await self.send_text(chat_id, text, **kwargs)

    async def send_poll(self, chat_id: str, question: str, options: list[str], **kwargs):
        if len(options) < 2 or len(options) > 10:
            raise ValueError("نظرسنجی باید بین ۲ تا ۱۰ گزینه داشته باشد.")
        payload = {"chat_id": chat_id, "question": question, "options": options,
                   "is_anonymous": kwargs.pop("is_anonymous", True),
                   "allows_multiple_answers": kwargs.pop("multi_select", False),
                   "type": "Regular"}
        payload.update({k: v for k, v in kwargs.items() if v is not None})
        return await self.request("sendPoll", payload)

    async def send_quiz(self, chat_id: str, question: str, options: list[str],
                        correct_option: int, **kwargs):
        if not 0 <= correct_option < len(options):
            raise ValueError("شماره گزینه صحیح نامعتبر است.")
        payload = {"chat_id": chat_id, "question": question, "options": options,
                   "correct_option_index": correct_option,
                   "is_anonymous": kwargs.pop("is_anonymous", True), "type": "Quiz"}
        if kwargs.get("hint"):
            payload["explanation"] = kwargs.pop("hint")
        payload.update({k: v for k, v in kwargs.items() if v is not None})
        return await self.request("sendPoll", payload)

    def _upload_sync(self, url: str, file: str | bytes, file_name: str):
        data = Path(file).read_bytes() if isinstance(file, str) else file
        if not isinstance(data, bytes):
            raise TypeError("file باید مسیر فایل یا bytes باشد.")
        boundary = "----IRubix" + secrets.token_hex(12)
        mime = mimetypes.guess_type(file_name)[0] or "application/octet-stream"
        body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{file_name}\"\r\n"
                f"Content-Type: {mime}\r\n\r\n").encode() + data + f"\r\n--{boundary}--\r\n".encode()
        req = urllib.request.Request(url, data=body, headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "IRubix/0.2.0"
        })
        try:
            with urllib.request.urlopen(req, timeout=max(self.timeout, 180)) as response:
                result = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise RubikaAPIError(f"آپلود فایل ناموفق بود: {exc}") from exc
        if result.get("status") != "OK" or not result.get("data", {}).get("file_id"):
            raise RubikaAPIError(result.get("dev_message") or "آپلود فایل ناموفق بود.")
        return result["data"]["file_id"]

    async def send_file(self, chat_id: str, path: str | bytes, text: str | None = None,
                        file_type: str = "File", **kwargs):
        name = kwargs.pop("file_name", None) or (Path(path).name if isinstance(path, str) else "upload.bin")
        upload = await self.request("requestSendFile", {"type": file_type})
        upload_url = upload.get("data", {}).get("upload_url")
        if not upload_url:
            raise RubikaAPIError("آدرس آپلود از روبیکا دریافت نشد.")
        file_id = await asyncio.to_thread(self._upload_sync, upload_url, path, name)
        payload = {"chat_id": chat_id, "file_id": file_id, "text": text or ""}
        payload.update({k: v for k, v in kwargs.items() if v is not None})
        return await self.request("sendFile", payload)

    def command(self, names):
        commands = [names] if isinstance(names, str) else list(names)
        commands = [str(x).lstrip("/") for x in commands]
        def decorator(func):
            self._handlers.append(("command", commands, func))
            return func
        return decorator

    def message(self, flt=None):
        def decorator(func):
            self._handlers.append(("message", flt, func))
            return func
        return decorator

    def callback(self):
        def decorator(func):
            self._handlers.append(("callback", None, func))
            return func
        return decorator

    async def _dispatch(self, raw: dict):
        event = Event(self, raw)
        for kind, value, handler in self._handlers:
            if kind == "command":
                first = event.text.strip().split(maxsplit=1)[0].lstrip("/") if event.text.strip() else ""
                if first not in value:
                    continue
            elif kind == "callback":
                if "button_id" not in raw and "data" not in raw and event.type != "InlineMessage":
                    continue
            elif kind == "message":
                if not event.text and not event.message:
                    continue
                if callable(value) and not value(event):
                    continue
            try:
                result = handler(self, event)
                if hasattr(result, "__await__"):
                    await result
            except Exception as exc:
                print(f"IRubix handler error: {exc}")

    async def start(self, poll_interval: float = 0.05):
        offset = format(int(time.time()), "08x") + secrets.token_hex(8)
        self._running = True
        print("IRubix bot started (polling).")
        while self._running:
            try:
                result = await self.request("getUpdates", {"offset_id": offset, "limit": 100})
                data = result.get("data", result) if isinstance(result, dict) else {}
                offset = data.get("next_offset_id", offset)
                for update in data.get("updates", []):
                    if isinstance(update, dict):
                        await self._dispatch(update)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                print(f"IRubix polling error: {exc}")
                await asyncio.sleep(1)
            await asyncio.sleep(poll_interval)

    def stop(self):
        self._running = False

    def run(self, poll_interval: float = 0.05):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            try:
                asyncio.run(self.start(poll_interval))
            except KeyboardInterrupt:
                self.stop()
                print("IRubix bot stopped.")
            return None
        return self.start(poll_interval)


Bot = IRubix
