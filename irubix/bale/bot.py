"""Async client for the Bale Bot API (stdlib only)."""
from __future__ import annotations

import asyncio
import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable

from .._token import resolve_token
from .._bot_api import BotAPIMethods, encode_request_payload


class BaleAPIError(RuntimeError):
    """Raised when Bale returns an API or transport error."""


class Event:
    """Incoming Bale update exposed to registered handlers."""

    def __init__(self, bot: "IRubix", raw: dict[str, Any]):
        self.bot = bot
        self.raw = raw
        self.update = raw
        self.message = raw.get("message") or raw.get("edited_message") or {}
        self.chat = self.message.get("chat") or {}
        self.chat_id = self.chat.get("id") or self.message.get("chat_id")
        self.message_id = self.message.get("message_id")
        self.text = self.message.get("text") or self.message.get("caption") or ""
        self.sender = self.message.get("from") or {}
        self.sender_id = self.sender.get("id")
        self.callback_query = raw.get("callback_query") or {}
        self.button_id = self.callback_query.get("data")
        self.type = "callback_query" if self.callback_query else (
            "message" if self.message else "unknown"
        )

    async def reply(self, text: str, **kwargs: Any):
        """Reply to the message that triggered this event."""
        if self.callback_query:
            chat = (self.callback_query.get("message") or {}).get("chat") or {}
            message_id = (self.callback_query.get("message") or {}).get("message_id")
            chat_id = chat.get("id")
        else:
            chat_id, message_id = self.chat_id, self.message_id
        if chat_id is None:
            raise BaleAPIError("Chat ID was not found in this update.")
        if message_id is not None:
            kwargs.setdefault("reply_to_message_id", message_id)
        return await self.bot.send_message(chat_id, text, **kwargs)


class IRubix(BotAPIMethods):
    """Async Bale Bot API client with a small, decorator-based interface."""

    API_URL = "https://tapi.bale.ai"
    FILE_URL = "https://tapi.bale.ai/file"
    __version__ = "0.4.0"

    def __init__(self, token: str | None = None, *, timeout: float = 40, base_url: str | None = None):
        self.token = resolve_token(token, "Bale")
        self.base_url = (base_url or self.API_URL).rstrip("/")
        self.timeout = timeout
        self._handlers: list[tuple[str, Any, Callable]] = []
        self._running = False
        self._offset: int | None = None

    def _request_sync(self, method: str, payload: dict | None = None):
        url = f"{self.base_url}/bot{self.token}/{method}"
        data, content_type = encode_request_payload(payload or {})
        request = urllib.request.Request(
            url, data=data,
            headers={"Content-Type": content_type, "Accept": "application/json",
                     "User-Agent": f"IRubix-Bale/{self.__version__}"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")
            raise BaleAPIError(f"HTTP {exc.code}: {detail}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise BaleAPIError(f"Connection error: {exc}") from exc
        try:
            result = json.loads(body)
        except json.JSONDecodeError as exc:
            raise BaleAPIError("Bale returned invalid JSON.") from exc
        if not isinstance(result, dict):
            raise BaleAPIError("Unexpected Bale API response.")
        if result.get("ok") is False:
            raise BaleAPIError(result.get("description") or "Bale API request failed.")
        return result.get("result", result)

    async def request(self, method: str, payload: dict | None = None):
        """Call a Bale Bot API method."""
        if not method or "/" in method:
            raise ValueError("Invalid API method name.")
        return await asyncio.to_thread(self._request_sync, method, payload)

    async def get_me(self):
        return await self.request("getMe")

    async def get_updates(self, *, offset: int | None = None, limit: int = 100,
                          timeout: int = 30):
        payload = {"limit": limit, "timeout": timeout}
        if offset is not None:
            payload["offset"] = offset
        return await self.request("getUpdates", payload)

    async def send_message(self, chat_id: int | str, text: str, **kwargs):
        payload = {"chat_id": chat_id, "text": text}
        for key in ("reply_to_message_id", "reply_markup", "parse_mode",
                    "disable_notification", "protect_content", "message_thread_id"):
            if kwargs.get(key) is not None:
                payload[key] = kwargs[key]
        return await self.request("sendMessage", payload)

    async def send_photo(self, chat_id: int | str, photo: str, caption: str | None = None,
                         **kwargs):
        payload = {"chat_id": chat_id, "photo": photo}
        if caption is not None:
            payload["caption"] = caption
        if kwargs.get("reply_to_message_id") is not None:
            payload["reply_to_message_id"] = kwargs["reply_to_message_id"]
        return await self.request("sendPhoto", payload)

    async def send_document(self, chat_id: int | str, document: str,
                            caption: str | None = None, **kwargs):
        payload = {"chat_id": chat_id, "document": document}
        if caption is not None:
            payload["caption"] = caption
        if kwargs.get("reply_to_message_id") is not None:
            payload["reply_to_message_id"] = kwargs["reply_to_message_id"]
        return await self.request("sendDocument", payload)

    async def edit_message_text(self, chat_id: int | str, message_id: int | str,
                                text: str, **kwargs):
        payload = {"chat_id": chat_id, "message_id": message_id, "text": text}
        if kwargs.get("reply_markup") is not None:
            payload["reply_markup"] = kwargs["reply_markup"]
        return await self.request("editMessageText", payload)

    async def delete_message(self, chat_id: int | str, message_id: int | str):
        return await self.request("deleteMessage", {
            "chat_id": chat_id, "message_id": message_id
        })

    def command(self, names: str | list[str]):
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

    def callback(self):
        def decorator(function):
            self._handlers.append(("callback", None, function))
            return function
        return decorator

    async def _dispatch(self, raw: dict):
        event = Event(self, raw)
        for kind, value, handler in tuple(self._handlers):
            if kind == "command":
                first = event.text.strip().split(maxsplit=1)[0].split("@", 1)[0].lstrip("/") if event.text.strip() else ""
                if not event.text.startswith("/") or first not in value:
                    continue
            elif kind == "callback":
                if not event.callback_query:
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
                print(f"[IRubix:Bale] Handler error: {exc}")

    async def start(self, *, timeout: int = 30, retry_delay: float = 2):
        """Start long polling until stop() is called."""
        if not 0 <= timeout <= 50:
            raise ValueError("timeout must be between 0 and 50 seconds.")
        state_dir = Path.home() / ".irubix" / "updates"
        token_key = hashlib.sha256(self.token.encode("utf-8")).hexdigest()
        state_file = state_dir / f"{token_key}.json"
        initialize_cursor = self._offset is None
        if self._offset is None:
            try:
                saved = json.loads(state_file.read_text(encoding="utf-8"))
                if isinstance(saved, dict) and isinstance(saved.get("offset_id"), int):
                    self._offset = saved["offset_id"]
                    initialize_cursor = False
            except (OSError, ValueError, TypeError):
                pass

        def save_offset():
            if self._offset is None:
                return
            try:
                state_dir.mkdir(parents=True, exist_ok=True)
                temporary = state_file.with_suffix(".tmp")
                temporary.write_text(json.dumps({"offset_id": self._offset}), encoding="utf-8")
                temporary.replace(state_file)
            except OSError:
                pass

        self._running = True
        print("[IRubix:Bale] Bot started.")
        while self._running:
            try:
                updates = await self.get_updates(
                    offset=self._offset,
                    timeout=0 if initialize_cursor else timeout,
                )
                batch = [item for item in (updates or []) if isinstance(item, dict)]
                if initialize_cursor:
                    # Drain only the backlog that existed before polling began.
                    # A zero-timeout request avoids swallowing new live messages.
                    for update in batch:
                        update_id = update.get("update_id")
                        if isinstance(update_id, int):
                            self._offset = max(self._offset or 0, update_id + 1)
                    save_offset()
                    if not batch:
                        initialize_cursor = False
                else:
                    for update in batch:
                        await self._dispatch(update)
                        update_id = update.get("update_id")
                        if isinstance(update_id, int):
                            self._offset = max(self._offset or 0, update_id + 1)
                            save_offset()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                print(f"[IRubix:Bale] Polling error: {exc}")
                await asyncio.sleep(retry_delay)
        print("[IRubix:Bale] Bot stopped.")

    def stop(self):
        """Stop the polling loop after the current request."""
        self._running = False

    def run(self, *, timeout: int = 30, retry_delay: float = 2):
        """Run polling; await the result if called inside an active event loop."""
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            try:
                asyncio.run(self.start(timeout=timeout, retry_delay=retry_delay))
            except KeyboardInterrupt:
                self.stop()
            return None
        return self.start(timeout=timeout, retry_delay=retry_delay)


Bot = IRubix
