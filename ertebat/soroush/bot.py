"""Async client for the Soroush Plus Bot API (stdlib only)."""
from __future__ import annotations

import asyncio
import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable, Optional

from .._token import resolve_token
from .._bot_api import BotAPIMethods, encode_request_payload


class SoroushAPIError(RuntimeError):
    """Raised when Soroush Plus returns an API or transport error."""


class Event:
    """Incoming Soroush update exposed to registered handlers."""

    def __init__(self, bot: "Ertebat", raw: dict):
        self.bot = bot
        self.raw = raw
        self.update = raw
        self.message = raw.get("message") or raw.get("edited_message") or {}
        self.callback_query = raw.get("callback_query") or {}
        if self.callback_query and not self.message:
            self.message = self.callback_query.get("message") or {}
        self.chat = self.message.get("chat") or {}
        self.chat_id = self.chat.get("id")
        self.message_id = self.message.get("message_id")
        self.text = self.message.get("text") or self.message.get("caption") or ""
        self.sender = self.message.get("from") or self.callback_query.get("from") or {}
        self.sender_id = self.sender.get("id")
        self.button_id = self.callback_query.get("data")
        self.type = "callback_query" if self.callback_query else (
            "message" if self.message else "unknown"
        )

    async def reply(self, text: str, **kwargs):
        """Reply to the message that triggered this event."""
        if self.chat_id is None:
            raise SoroushAPIError("Chat ID was not found in this update.")
        if self.message_id is not None:
            kwargs.setdefault("reply_to_message_id", self.message_id)
        return await self.bot.send_message(self.chat_id, text, **kwargs)


class Ertebat(BotAPIMethods):
    """Async Soroush Plus Bot API client with decorator-based handlers."""

    API_URL = "https://api.splus.ir"
    FILE_URL = "https://api.splus.ir/file"
    __version__ = "0.5.0"

    def __init__(self, token: str | None = None, *, timeout: float = 40,
                 base_url: Optional[str] = None):
        self.token = resolve_token(token, "Soroush Plus")
        self.base_url = (base_url or self.API_URL).rstrip("/")
        self.timeout = timeout
        self._handlers = []
        self._running = False
        self._offset = None

    def _request_sync(self, method: str, payload: Optional[dict] = None,
                      http_method: str = "POST"):
        if not method or "/" in method:
            raise ValueError("Invalid API method name.")
        url = f"{self.base_url}/bot{self.token}/{method}"
        data = None
        headers = {"Accept": "application/json",
                   "User-Agent": f"Ertebat-Soroush/{self.__version__}"}
        if http_method.upper() == "GET":
            if payload:
                url += "?" + urllib.parse.urlencode(payload, doseq=True)
        else:
            data, content_type = encode_request_payload(payload or {})
            headers["Content-Type"] = content_type
        request = urllib.request.Request(url, data=data, headers=headers,
                                         method=http_method.upper())
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")
            raise SoroushAPIError(f"HTTP {exc.code}: {detail}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise SoroushAPIError(f"Connection error: {exc}") from exc
        try:
            result = json.loads(body)
        except json.JSONDecodeError as exc:
            raise SoroushAPIError("Soroush Plus returned invalid JSON.") from exc
        if not isinstance(result, dict):
            raise SoroushAPIError("Unexpected Soroush Plus API response.")
        ok = result.get("ok", result.get("OK"))
        if ok is False:
            description = result.get("description") or "Soroush Plus API request failed."
            code = result.get("error_code")
            raise SoroushAPIError(f"{description} (error_code={code})" if code else description)
        return result.get("result", result)

    async def request(self, method: str, payload: Optional[dict] = None,
                      http_method: str = "POST"):
        """Call a Soroush Plus Bot API method."""
        return await asyncio.to_thread(self._request_sync, method, payload, http_method)

    async def get_me(self):
        return await self.request("getMe")

    async def log_out(self):
        return await self.request("logOut")

    async def close(self):
        return await self.request("close")

    async def get_updates(self, *, offset: Optional[int] = None, limit: int = 100,
                          timeout: int = 30, allowed_updates=None):
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100.")
        if timeout < 0:
            raise ValueError("timeout must be zero or greater.")
        payload = {"limit": limit, "timeout": timeout}
        if offset is not None:
            payload["offset"] = offset
        if allowed_updates is not None:
            payload["allowed_updates"] = json.dumps(allowed_updates)
        return await self.request("getUpdates", payload)

    async def set_webhook(self, url: str, **kwargs):
        if not isinstance(url, str):
            raise TypeError("url must be a string.")
        payload = {"url": url}
        for key in ("ip_address", "max_connections", "drop_pending_updates",
                    "allowed_updates", "certificate"):
            if kwargs.get(key) is not None:
                value = kwargs[key]
                payload[key] = json.dumps(value) if key == "allowed_updates" else value
        return await self.request("setWebhook", payload)

    async def delete_webhook(self, *, drop_pending_updates: Optional[bool] = None):
        payload = {}
        if drop_pending_updates is not None:
            payload["drop_pending_updates"] = drop_pending_updates
        return await self.request("deleteWebhook", payload)

    async def get_webhook_info(self):
        return await self.request("getWebhookInfo")

    async def send_message(self, chat_id, text: str, **kwargs):
        payload = {"chat_id": chat_id, "text": text}
        payload.update({key: value for key, value in kwargs.items() if value is not None})
        return await self.request("sendMessage", payload)

    async def forward_message(self, chat_id, from_chat_id, message_id, **kwargs):
        payload = {
            "chat_id": chat_id, "from_chat_id": from_chat_id, "message_id": message_id
        }
        payload.update({key: value for key, value in kwargs.items() if value is not None})
        return await self.request("forwardMessage", payload)

    async def send_photo(self, chat_id, photo, caption: Optional[str] = None, **kwargs):
        payload = {"chat_id": chat_id, "photo": photo}
        if caption is not None:
            payload["caption"] = caption
        payload.update({key: value for key, value in kwargs.items() if value is not None})
        return await self.request("sendPhoto", payload)

    async def send_document(self, chat_id, document, caption: Optional[str] = None, **kwargs):
        payload = {"chat_id": chat_id, "document": document}
        if caption is not None:
            payload["caption"] = caption
        for key in ("parse_mode", "reply_markup", "reply_to_message_id"):
            if kwargs.get(key) is not None:
                payload[key] = kwargs[key]
        return await self.request("sendDocument", payload)

    async def edit_message_text(self, chat_id, message_id, text: str, **kwargs):
        payload = {"chat_id": chat_id, "message_id": message_id, "text": text}
        payload.update({key: value for key, value in kwargs.items() if value is not None})
        return await self.request("editMessageText", payload)

    async def delete_message(self, chat_id, message_id):
        return await self.request("deleteMessage", {
            "chat_id": chat_id, "message_id": message_id
        })

    async def answer_callback_query(self, callback_query_id: str, **kwargs):
        payload = {"callback_query_id": callback_query_id}
        for key in ("text", "show_alert", "url", "cache_time"):
            if kwargs.get(key) is not None:
                payload[key] = kwargs[key]
        return await self.request("answerCallbackQuery", payload)

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
                print(f"[Ertebat:Soroush] Handler error: {exc}")

    async def start(self, *, timeout: int = 30, retry_delay: float = 2):
        """Start long polling until stop() is called."""
        state_dir = Path.home() / ".ertebat" / "updates"
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
        print("[Ertebat:Soroush] Bot started.")
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
                print(f"[Ertebat:Soroush] Polling error: {exc}")
                await asyncio.sleep(retry_delay)
        print("[Ertebat:Soroush] Bot stopped.")

    def stop(self):
        self._running = False

    def run(self, *, timeout: int = 30, retry_delay: float = 2):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            try:
                asyncio.run(self.start(timeout=timeout, retry_delay=retry_delay))
            except KeyboardInterrupt:
                self.stop()
            return None
        return self.start(timeout=timeout, retry_delay=retry_delay)


Bot = Ertebat
