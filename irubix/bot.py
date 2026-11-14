"""Fast, dependency-free client for the official Rubika Bot API."""
from __future__ import annotations

import asyncio
import json
import mimetypes
import secrets
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable


class RubikaAPIError(RuntimeError):
    """Raised when the Rubika Bot API returns an error."""


class Event:
    """A normalized incoming update passed to event handlers."""

    def __init__(self, bot: "IRubix", raw: dict[str, Any]):
        self.bot = bot
        self.raw = raw
        self.update = raw
        self.type = raw.get("type", "")
        message = (
            raw.get("message")
            or raw.get("new_message")
            or raw.get("updated_message")
            or {}
        )
        self.message = message if isinstance(message, dict) else {}
        chat = self.message.get("chat") or {}
        self.chat_id = (
            raw.get("chat_id")
            or self.message.get("chat_id")
            or (chat.get("chat_id") if isinstance(chat, dict) else None)
        )
        self.message_id = self.message.get("message_id") or raw.get("message_id")
        self.text = self.message.get("text") or raw.get("text") or ""
        self.sender_id = (
            self.message.get("sender_id")
            or self.message.get("author_object_guid")
            or raw.get("sender_id")
            or raw.get("user_id")
        )
        self.button_id = raw.get("button_id") or raw.get("data")
        self.update_type = self.type

    async def reply(self, text: str, **kwargs: Any):
        """Reply to the current message."""
        if not self.chat_id:
            raise RubikaAPIError("Chat ID was not found in this update.")
        if self.message_id:
            kwargs.setdefault("reply_to_message_id", self.message_id)
        return await self.bot.send_text(self.chat_id, text, **kwargs)


class IRubix:
    """Async Rubika Bot API client. Uses only the Python standard library."""

    API_URL = "https://botapi.rubika.ir/v3"
    __version__ = "0.3.0"

    def __init__(
        self,
        token: str,
        *,
        timeout: float = 30,
        base_url: str | None = None,
    ):
        if not isinstance(token, str) or not token.strip():
            raise ValueError("Bot token must not be empty.")
        self.token = token.strip()
        self.base_url = (base_url or self.API_URL).rstrip("/") + "/" + self.token
        self.timeout = timeout
        self._handlers: list[tuple[str, Any, Callable]] = []
        self._running = False

    def _request_sync(self, method: str, payload: dict | None = None):
        """Internal synchronous HTTP request; called in a worker thread."""
        url = self.base_url + "/" + method
        body = json.dumps(payload or {}, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": f"IRubix/{self.__version__}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")
            raise RubikaAPIError(f"HTTP {exc.code}: {detail}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise RubikaAPIError(f"Connection error: {exc}") from exc

        try:
            result = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RubikaAPIError("Rubika returned an invalid JSON response.") from exc

        if isinstance(result, dict):
            status = result.get("status")
            if status not in (None, "OK"):
                message = result.get("dev_message") or result.get("message") or status
                raise RubikaAPIError(str(message))
        return result

    async def request(self, method: str, input: dict | None = None):
        """Call any official Bot API method asynchronously."""
        if not method or "/" in method:
            raise ValueError("Invalid API method name.")
        return await asyncio.to_thread(self._request_sync, method, input)

    async def get_me(self):
        """Return bot information using getMe."""
        return await self.request("getMe")

    async def get_chat(self, chat_id: str):
        """Return information about a chat using getChat."""
        return await self.request("getChat", {"chat_id": chat_id})

    async def get_file(self, file_id: str):
        """Get a file download URL using getFile."""
        return await self.request("getFile", {"file_id": file_id})

    async def send_text(self, chat_id: str, text: str, **kwargs):
        """Send a text message. Supports keypad and reply options."""
        payload = {"chat_id": chat_id, "text": text}
        allowed = (
            "metadata",
            "chat_keypad",
            "inline_keypad",
            "reply_to_message_id",
            "disable_notification",
            "chat_keypad_type",
        )
        payload.update(
            {key: value for key, value in kwargs.items()
             if key in allowed and value is not None}
        )
        return await self.request("sendMessage", payload)

    async def send_message(self, chat_id: str, text: str, **kwargs):
        """Alias for send_text."""
        return await self.send_text(chat_id, text, **kwargs)

    async def send_poll(self, chat_id: str, question: str, options: list[str]):
        """Send a poll using the documented sendPoll parameters."""
        if not isinstance(options, list) or len(options) < 2:
            raise ValueError("A poll needs at least two options.")
        return await self.request(
            "sendPoll",
            {"chat_id": chat_id, "question": question, "options": options},
        )

    async def send_quiz(self, *args, **kwargs):
        """Quiz mode is not documented by the current official Bot API."""
        raise NotImplementedError(
            "The current official Rubika Bot API documents sendPoll, not quiz mode."
        )

    async def forward_message(
        self,
        from_chat_id: str,
        message_id: str,
        to_chat_id: str,
        disable_notification: bool = False,
    ):
        """Forward a message to another chat."""
        return await self.request(
            "forwardMessage",
            {
                "from_chat_id": from_chat_id,
                "message_id": message_id,
                "to_chat_id": to_chat_id,
                "disable_notification": disable_notification,
            },
        )

    async def edit_message_text(self, chat_id: str, message_id: str, text: str):
        """Edit a message previously sent by the bot."""
        return await self.request(
            "editMessageText",
            {"chat_id": chat_id, "message_id": message_id, "text": text},
        )

    async def delete_message(self, chat_id: str, message_id: str):
        """Delete a message using deleteMessage."""
        return await self.request(
            "deleteMessage", {"chat_id": chat_id, "message_id": message_id}
        )

    async def ban_chat_member(self, chat_id: str, user_id: str):
        """Ban a user from a group or channel."""
        return await self.request(
            "banChatMember", {"chat_id": chat_id, "user_id": user_id}
        )

    async def unban_chat_member(self, chat_id: str, user_id: str):
        """Unban a user from a group or channel."""
        return await self.request(
            "unbanChatMember", {"chat_id": chat_id, "user_id": user_id}
        )

    def _upload_sync(self, upload_url: str, file: str | bytes, file_name: str):
        content = Path(file).read_bytes() if isinstance(file, (str, Path)) else file
        if not isinstance(content, bytes):
            raise TypeError("file must be a file path or bytes.")
        boundary = "----IRubix" + secrets.token_hex(12)
        mime = mimetypes.guess_type(file_name)[0] or "application/octet-stream"
        header = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{file_name}"\r\n'
            f"Content-Type: {mime}\r\n\r\n"
        ).encode("utf-8")
        body = header + content + f"\r\n--{boundary}--\r\n".encode("ascii")
        request = urllib.request.Request(
            upload_url,
            data=body,
            headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "User-Agent": f"IRubix/{self.__version__}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=max(self.timeout, 180)) as response:
                result = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise RubikaAPIError(f"File upload failed: {exc}") from exc

        data = result.get("data") or result
        file_id = data.get("file_id") if isinstance(data, dict) else None
        if not file_id:
            raise RubikaAPIError("Rubika did not return a file_id after upload.")
        return file_id

    async def send_file(
        self,
        chat_id: str,
        path: str | Path | bytes,
        text: str | None = None,
        file_type: str = "File",
        **kwargs,
    ):
        """Upload a file, then send it with sendFile."""
        name = kwargs.pop("file_name", None)
        if not name:
            name = Path(path).name if isinstance(path, (str, Path)) else "upload.bin"
        upload_result = await self.request("requestSendFile", {"type": file_type})
        upload_data = upload_result.get("data") or upload_result
        upload_url = upload_data.get("upload_url") if isinstance(upload_data, dict) else None
        if not upload_url:
            raise RubikaAPIError("Rubika did not return an upload_url.")
        file_id = await asyncio.to_thread(
            self._upload_sync, upload_url, path, str(name)
        )
        payload = {"chat_id": chat_id, "file_id": file_id}
        if text is not None:
            payload["text"] = text
        allowed = (
            "reply_to_message_id",
            "disable_notification",
            "chat_keypad",
            "inline_keypad",
            "chat_keypad_type",
        )
        payload.update(
            {key: value for key, value in kwargs.items()
             if key in allowed and value is not None}
        )
        return await self.request("sendFile", payload)

    def command(self, names):
        """Register one or more slash commands."""
        commands = [names] if isinstance(names, str) else list(names)
        commands = [str(item).lstrip("/") for item in commands]

        def decorator(function):
            self._handlers.append(("command", commands, function))
            return function
        return decorator

    def message(self, flt=None):
        """Register a message handler. An optional callable filters events."""
        def decorator(function):
            self._handlers.append(("message", flt, function))
            return function
        return decorator

    def callback(self):
        """Register an inline-keyboard callback handler."""
        def decorator(function):
            self._handlers.append(("callback", None, function))
            return function
        return decorator

    async def _dispatch(self, raw: dict):
        event = Event(self, raw)
        for kind, value, handler in tuple(self._handlers):
            if kind == "command":
                first = (
                    event.text.strip().split(maxsplit=1)[0].lstrip("/")
                    if event.text.strip() else ""
                )
                if first not in value:
                    continue
            elif kind == "callback":
                if not (
                    "button_id" in raw
                    or "data" in raw
                    or event.type == "InlineMessage"
                ):
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
                print(f"[IRubix] Handler error: {exc}")

    async def start(self, poll_interval: float = 1.0, limit: int = 100):
        """Start long-running getUpdates polling."""
        if poll_interval < 0.1:
            raise ValueError("poll_interval must be at least 0.1 seconds.")
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100.")
        offset = None
        self._running = True
        print("[IRubix] Bot started.")
        while self._running:
            payload = {"limit": limit}
            if offset:
                payload["offset_id"] = offset
            try:
                result = await self.request("getUpdates", payload)
                data = result.get("data") or result
                if not isinstance(data, dict):
                    await asyncio.sleep(poll_interval)
                    continue
                offset = data.get("next_offset_id") or offset
                for update in data.get("updates") or []:
                    if isinstance(update, dict):
                        await self._dispatch(update)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                print(f"[IRubix] Polling error: {exc}")
                await asyncio.sleep(2)
            await asyncio.sleep(poll_interval)
        print("[IRubix] Bot stopped.")

    def stop(self):
        """Ask the polling loop to stop."""
        self._running = False

    def run(self, poll_interval: float = 1.0, limit: int = 100):
        """Run polling; inside an active event loop, await the returned coroutine."""
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            try:
                asyncio.run(self.start(poll_interval, limit))
            except KeyboardInterrupt:
                self.stop()
            return None
        return self.start(poll_interval, limit)


Bot = IRubix
