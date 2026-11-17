"""Async Telegram Bot API client (Python standard library only)."""
from __future__ import annotations
import asyncio, hashlib, json, urllib.error, urllib.request
from pathlib import Path
from typing import Any, Callable
from .._token import resolve_token
from .._bot_api import BotAPIMethods, encode_request_payload

class TelegramAPIError(RuntimeError):
    """Raised for Telegram API and transport errors."""

class Event:
    def __init__(self, bot: "Ertebat", raw: dict[str, Any]):
        self.bot, self.raw, self.update = bot, raw, raw
        self.message = raw.get("message") or raw.get("edited_message") or raw.get("channel_post") or raw.get("edited_channel_post") or {}
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
        self.callback_query_id = self.callback_query.get("id")
        self.type = "callback_query" if self.callback_query else ("message" if self.message else "unknown")

    async def reply(self, text: str, **kwargs: Any):
        if self.chat_id is None:
            raise TelegramAPIError("Chat ID was not found in this update.")
        if self.message_id is not None:
            kwargs.setdefault("reply_parameters", {"message_id": self.message_id})
        return await self.bot.send_message(self.chat_id, text, **kwargs)

class Ertebat(BotAPIMethods):
    """Async Telegram Bot API client with decorator-based handlers."""
    API_URL = "https://api.telegram.org"
    FILE_URL = "https://api.telegram.org/file"
    __version__ = "0.1.0"

    def __init__(self, token: str | None = None, *, timeout: float = 40, base_url: str | None = None):
        self.token = resolve_token(token, "Telegram")
        self.base_url = (base_url or self.API_URL).rstrip("/")
        self.timeout = timeout
        self._handlers: list[tuple[str, Any, Callable]] = []
        self._running = False
        self._offset: int | None = None

    def _request_sync(self, method: str, payload: dict | None = None):
        if not method or "/" in method:
            raise ValueError("Invalid API method name.")
        url = f"{self.base_url}/bot{self.token}/{method}"
        body, content_type = encode_request_payload(payload or {})
        request = urllib.request.Request(url, data=body, headers={
            "Content-Type": content_type, "Accept": "application/json",
            "User-Agent": f"Ertebat-Telegram/{self.__version__}"}, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raise TelegramAPIError(f"HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise TelegramAPIError(f"Connection error: {exc}") from exc
        try:
            result = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise TelegramAPIError("Telegram returned invalid JSON.") from exc
        if not isinstance(result, dict) or result.get("ok") is not True:
            description = result.get("description", "Telegram API request failed.") if isinstance(result, dict) else "Unexpected Telegram API response."
            code = result.get("error_code") if isinstance(result, dict) else None
            raise TelegramAPIError(f"{description} (error_code={code})" if code else description)
        return result.get("result")

    async def request(self, method: str, payload: dict | None = None):
        if not method or "/" in method:
            raise ValueError("Invalid API method name.")
        return await asyncio.to_thread(self._request_sync, method, payload)

    async def get_me(self): return await self.request("getMe")
    async def get_chat(self, chat_id): return await self.request("getChat", {"chat_id": chat_id})

    async def get_updates(self, *, offset: int | None = None, limit: int = 100, timeout: int = 30, allowed_updates=None):
        if not 1 <= limit <= 100: raise ValueError("limit must be between 1 and 100.")
        if timeout < 0: raise ValueError("timeout must be zero or greater.")
        payload = {"limit": limit, "timeout": timeout}
        if offset is not None: payload["offset"] = offset
        if allowed_updates is not None: payload["allowed_updates"] = allowed_updates
        return await self.request("getUpdates", payload)

    async def send_message(self, chat_id, text: str, **kwargs):
        payload = {"chat_id": chat_id, "text": text}
        payload.update({k: v for k, v in kwargs.items() if v is not None})
        return await self.request("sendMessage", payload)

    async def send_photo(self, chat_id, photo, caption: str | None = None, **kwargs):
        payload = {"chat_id": chat_id, "photo": photo}
        if caption is not None: payload["caption"] = caption
        payload.update({k: v for k, v in kwargs.items() if v is not None})
        return await self.request("sendPhoto", payload)

    async def send_document(self, chat_id, document, caption: str | None = None, **kwargs):
        payload = {"chat_id": chat_id, "document": document}
        if caption is not None: payload["caption"] = caption
        for k in ("parse_mode", "reply_markup", "reply_parameters", "message_thread_id", "disable_notification"):
            if kwargs.get(k) is not None: payload[k] = kwargs[k]
        return await self.request("sendDocument", payload)

    async def forward_message(self, chat_id, from_chat_id, message_id, **kwargs):
        payload = {"chat_id": chat_id, "from_chat_id": from_chat_id, "message_id": message_id}
        for k in ("message_thread_id", "disable_notification", "protect_content"):
            if kwargs.get(k) is not None: payload[k] = kwargs[k]
        return await self.request("forwardMessage", payload)

    async def edit_message_text(self, chat_id, message_id, text: str, **kwargs):
        payload = {"chat_id": chat_id, "message_id": message_id, "text": text}
        payload.update({k: v for k, v in kwargs.items() if v is not None})
        return await self.request("editMessageText", payload)

    async def delete_message(self, chat_id, message_id):
        return await self.request("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

    async def answer_callback_query(self, callback_query_id: str, **kwargs):
        payload = {"callback_query_id": callback_query_id}
        for k in ("text", "show_alert", "url", "cache_time"):
            if kwargs.get(k) is not None: payload[k] = kwargs[k]
        return await self.request("answerCallbackQuery", payload)

    def command(self, names):
        commands = [names] if isinstance(names, str) else list(names)
        commands = [str(n).lstrip("/") for n in commands]
        def decorator(fn):
            self._handlers.append(("command", commands, fn)); return fn
        return decorator

    def message(self, flt=None):
        def decorator(fn):
            self._handlers.append(("message", flt, fn)); return fn
        return decorator

    def callback(self):
        def decorator(fn):
            self._handlers.append(("callback", None, fn)); return fn
        return decorator

    async def _dispatch(self, raw: dict[str, Any]):
        event = Event(self, raw)
        for kind, value, handler in tuple(self._handlers):
            if kind == "command":
                first = event.text.strip().split(maxsplit=1)[0].split("@", 1)[0].lstrip("/") if event.text.strip() else ""
                if not event.text.startswith("/") or first not in value: continue
            elif kind == "callback":
                if not event.callback_query: continue
            elif kind == "message":
                if not event.message or (callable(value) and not value(event)): continue
            try:
                result = handler(self, event)
                if hasattr(result, "__await__"): await result
            except Exception as exc:
                print(f"[Ertebat:Telegram] Handler error: {exc}")

    async def start(self, *, timeout: int = 30, retry_delay: float = 2):
        """Long polling; Telegram webhooks and getUpdates cannot be used together."""
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
        print("[Ertebat:Telegram] Bot started.")
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
            except asyncio.CancelledError: raise
            except Exception as exc:
                print(f"[Ertebat:Telegram] Polling error: {exc}")
                await asyncio.sleep(retry_delay)
        print("[Ertebat:Telegram] Bot stopped.")

    def stop(self): self._running = False

    def run(self, *, timeout: int = 30, retry_delay: float = 2):
        try: asyncio.get_running_loop()
        except RuntimeError:
            try: asyncio.run(self.start(timeout=timeout, retry_delay=retry_delay))
            except KeyboardInterrupt: self.stop()
            return None
        return self.start(timeout=timeout, retry_delay=retry_delay)

Bot = Ertebat
