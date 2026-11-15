"""Optional, platform-neutral utilities for IRubix applications.

These helpers use dependency injection and the Python standard library only.
They do not claim to add API features that a messaging platform does not expose.
"""
from __future__ import annotations

import asyncio
import importlib.util
import inspect
import json
import logging
import os
import time
import uuid
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Awaitable, Callable


class PluginManager:
    """Load and manage Python plugin modules from local .py files or packages."""

    def __init__(self, app: Any = None):
        self.app = app
        self.plugins: dict[str, Any] = {}

    def load(self, path: str | os.PathLike, *, name: str | None = None):
        path = Path(path).expanduser().resolve()
        if not path.is_file() or path.suffix != ".py":
            raise FileNotFoundError(f"Plugin must be an existing .py file: {path}")
        plugin_name = name or path.stem
        if plugin_name in self.plugins:
            raise ValueError(f"Plugin {plugin_name!r} is already loaded.")
        module_name = f"_irubix_plugin_{plugin_name}_{uuid.uuid4().hex}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load plugin from {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        setup = getattr(module, "setup", None)
        if setup is not None:
            result = setup(self.app)
            if inspect.isawaitable(result):
                raise TypeError("Async plugin setup is not supported by load(); call setup manually.")
        self.plugins[plugin_name] = module
        return module

    def unload(self, name: str):
        try:
            module = self.plugins.pop(name)
        except KeyError as exc:
            raise KeyError(f"Plugin {name!r} is not loaded.") from exc
        teardown = getattr(module, "teardown", None)
        if teardown is not None:
            result = teardown(self.app)
            if inspect.isawaitable(result):
                raise TypeError("Async teardown is not supported by unload().")
        return module

    def list(self):
        return tuple(self.plugins)


class MiddlewareManager:
    """Run async/sync middleware in registration order around a handler."""

    def __init__(self):
        self._items: list[Callable] = []

    def add(self, middleware: Callable):
        if not callable(middleware):
            raise TypeError("middleware must be callable")
        self._items.append(middleware)
        return middleware

    def remove(self, middleware: Callable):
        self._items.remove(middleware)

    async def execute(self, handler: Callable, *args, **kwargs):
        async def invoke(index: int):
            if index == len(self._items):
                result = handler(*args, **kwargs)
            else:
                middleware = self._items[index]
                result = middleware(*args, lambda: invoke(index + 1))
            return await result if inspect.isawaitable(result) else result
        return await invoke(0)


class RateLimiter:
    """Per-key asynchronous token-bucket rate limiter."""

    def __init__(self, rate: float, per: float = 1.0, *, capacity: float | None = None):
        if rate <= 0 or per <= 0:
            raise ValueError("rate and per must be positive")
        self.rate = float(rate) / float(per)
        self.capacity = float(capacity if capacity is not None else rate)
        if self.capacity <= 0:
            raise ValueError("capacity must be positive")
        self._buckets: dict[Any, tuple[float, float]] = {}
        self._lock = asyncio.Lock()

    async def acquire(self, key: Any = "default", tokens: float = 1.0):
        if tokens <= 0 or tokens > self.capacity:
            raise ValueError("tokens must be positive and no greater than capacity")
        while True:
            async with self._lock:
                now = time.monotonic()
                available, updated = self._buckets.get(key, (self.capacity, now))
                available = min(self.capacity, available + (now - updated) * self.rate)
                if available >= tokens:
                    self._buckets[key] = (available - tokens, now)
                    return
                wait = (tokens - available) / self.rate
                self._buckets[key] = (available, now)
            await asyncio.sleep(wait)

    def try_acquire(self, key: Any = "default", tokens: float = 1.0) -> bool:
        if tokens <= 0 or tokens > self.capacity:
            raise ValueError("tokens must be positive and no greater than capacity")
        now = time.monotonic()
        available, updated = self._buckets.get(key, (self.capacity, now))
        available = min(self.capacity, available + (now - updated) * self.rate)
        if available < tokens:
            self._buckets[key] = (available, now)
            return False
        self._buckets[key] = (available - tokens, now)
        return True


class ConversationManager:
    """Track per-chat conversation state and await the next supplied message."""

    def __init__(self):
        self._states: dict[str, dict[str, Any]] = {}
        self._queues: dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)

    @staticmethod
    def _key(chat_id: Any) -> str:
        if chat_id is None:
            raise ValueError("chat_id is required")
        return str(chat_id)

    def begin(self, chat_id: Any, *, data: dict | None = None):
        key = self._key(chat_id)
        self._states[key] = dict(data or {})
        return self._states[key]

    def active(self, chat_id: Any) -> bool:
        return self._key(chat_id) in self._states

    def get(self, chat_id: Any, name: str | None = None, default=None):
        state = self._states.get(self._key(chat_id))
        if state is None:
            return default if name is not None else None
        return state.get(name, default) if name is not None else dict(state)

    def set(self, chat_id: Any, name: str, value: Any):
        key = self._key(chat_id)
        if key not in self._states:
            self.begin(key)
        self._states[key][name] = value
        return value

    async def feed(self, chat_id: Any, message: Any):
        key = self._key(chat_id)
        if key in self._states:
            await self._queues[key].put(message)
            return True
        return False

    async def wait(self, chat_id: Any, *, timeout: float | None = None):
        key = self._key(chat_id)
        if key not in self._states:
            raise RuntimeError("No active conversation for this chat")
        if timeout is None:
            return await self._queues[key].get()
        return await asyncio.wait_for(self._queues[key].get(), timeout)

    def end(self, chat_id: Any):
        key = self._key(chat_id)
        self._states.pop(key, None)
        queue = self._queues.pop(key, None)
        if queue is not None:
            while not queue.empty():
                queue.get_nowait()


class BotStats:
    """Small in-memory counters and uptime tracker."""

    def __init__(self):
        self.started_at = time.monotonic()
        self._counts = Counter()
        self._errors = Counter()

    def record_message(self, platform: str = "unknown", count: int = 1):
        self._counts[str(platform)] += count

    def record_error(self, category: str = "general", count: int = 1):
        self._errors[str(category)] += count

    def snapshot(self):
        return {
            "uptime_seconds": round(time.monotonic() - self.started_at, 3),
            "messages": dict(self._counts),
            "errors": dict(self._errors),
            "total_messages": sum(self._counts.values()),
            "total_errors": sum(self._errors.values()),
        }


class CommandPermissions:
    """Simple role/permission checks; persistence is intentionally left to callers."""

    def __init__(self):
        self._roles: dict[str, set[str]] = defaultdict(set)
        self._grants: dict[str, set[str]] = defaultdict(set)

    def set_role(self, user_id: Any, role: str):
        self._roles[str(user_id)] = {str(role)}

    def grant(self, user_id: Any, permission: str):
        self._grants[str(user_id)].add(str(permission))

    def revoke(self, user_id: Any, permission: str):
        self._grants[str(user_id)].discard(str(permission))

    def allows(self, user_id: Any, permission: str, *, roles: tuple[str, ...] = ("admin", "owner")):
        user = str(user_id)
        return permission in self._grants[user] or bool(self._roles[user].intersection(roles))


class MessageBuilder:
    """Build a platform-neutral message and send supported parts through a client."""

    def __init__(self, text: str = ""):
        self.text = text
        self.files: list[tuple[Any, str]] = []
        self.reply_to = None
        self.options: dict[str, Any] = {}

    def add_text(self, text: str):
        self.text += str(text)
        return self

    def add_file(self, file: Any, *, file_type: str = "File"):
        self.files.append((file, file_type))
        return self

    def reply_to_message(self, message_id: Any):
        self.reply_to = message_id
        return self

    def option(self, **kwargs):
        self.options.update(kwargs)
        return self

    async def send(self, bot: Any, chat_id: str):
        results = []
        if self.text:
            sender = getattr(bot, "send_text", None) or getattr(bot, "send_message", None)
            if sender is None:
                raise NotImplementedError("This client has no text-send method")
            options = dict(self.options)
            if self.reply_to is not None:
                options.setdefault("reply_to_message_id", self.reply_to)
            results.append(await sender(chat_id, self.text, **options))
        for file, file_type in self.files:
            sender = getattr(bot, "send_file", None)
            if sender is None:
                raise NotImplementedError("This client has no file-send method")
            results.append(await sender(chat_id, file, text=self.text or None, file_type=file_type))
        return results


class FileManager:
    """Safe local file helper rooted at a caller-selected directory."""

    def __init__(self, root: str | os.PathLike):
        self.root = Path(root).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, name: str):
        path = (self.root / name).resolve()
        if path != self.root and self.root not in path.parents:
            raise ValueError("Path escapes the configured storage root")
        return path

    def save(self, name: str, content: bytes | str):
        path = self._path(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = content.encode("utf-8") if isinstance(content, str) else content
        if not isinstance(data, bytes):
            raise TypeError("content must be bytes or str")
        path.write_bytes(data)
        return path

    def read(self, name: str, *, text: bool = False):
        data = self._path(name).read_bytes()
        return data.decode("utf-8") if text else data

    def delete(self, name: str):
        path = self._path(name)
        path.unlink()
        return True


class AIAdapter:
    """Provider-neutral AI bridge around a caller-supplied sync or async function."""

    def __init__(self, generate: Callable[[str], Any]):
        if not callable(generate):
            raise TypeError("generate must be callable")
        self.generate = generate

    async def ask(self, prompt: str):
        result = self.generate(prompt)
        return await result if inspect.isawaitable(result) else result


class CloudStorageAdapter:
    """Cloud storage bridge using injected upload/download callables."""

    def __init__(self, upload: Callable, download: Callable):
        if not callable(upload) or not callable(download):
            raise TypeError("upload and download must be callable")
        self._upload, self._download = upload, download

    async def upload(self, name: str, content: bytes):
        result = self._upload(name, content)
        return await result if inspect.isawaitable(result) else result

    async def download(self, name: str):
        result = self._download(name)
        return await result if inspect.isawaitable(result) else result


class AutoReconnect:
    """Restart a client's async start() loop after failures with bounded backoff."""

    def __init__(self, client: Any, *, initial_delay: float = 1.0,
                 max_delay: float = 30.0, max_retries: int | None = None):
        if initial_delay <= 0 or max_delay < initial_delay:
            raise ValueError("Invalid reconnect delays")
        self.client = client
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.max_retries = max_retries

    async def run(self):
        retries, delay = 0, self.initial_delay
        while self.max_retries is None or retries <= self.max_retries:
            try:
                return await self.client.start()
            except asyncio.CancelledError:
                raise
            except Exception:
                retries += 1
                if self.max_retries is not None and retries > self.max_retries:
                    raise
                await asyncio.sleep(delay)
                delay = min(self.max_delay, delay * 2)


class WebhookAdapter:
    """Validate an incoming webhook secret and pass decoded updates to a handler.

    This is a framework-neutral request adapter, not an HTTP server. Mount handle()
    in the ASGI/framework server chosen by the application.
    """

    def __init__(self, handler: Callable[[dict], Any], secret: str):
        if not callable(handler) or not secret:
            raise ValueError("A handler and non-empty secret are required")
        self.handler, self.secret = handler, secret

    async def handle(self, payload: dict, secret: str):
        import hmac
        if not hmac.compare_digest(str(secret), self.secret):
            raise PermissionError("Invalid webhook secret")
        result = self.handler(payload)
        return await result if inspect.isawaitable(result) else result


class DeveloperConsole:
    """Configure readable standard-library logging for an IRubix application."""

    @staticmethod
    def configure(level: int = logging.INFO, *, logger: str = "irubix"):
        instance = logging.getLogger(logger)
        if not instance.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("[IRubix] %(levelname)s: %(message)s"))
            instance.addHandler(handler)
        instance.setLevel(level)
        return instance


class SmartErrorHandler:
    """Log exceptions with context and optionally invoke an application callback."""

    def __init__(self, callback: Callable | None = None, *, logger=None):
        self.callback = callback
        self.logger = logger or logging.getLogger("irubix")

    async def handle(self, error: BaseException, *, context: Any = None):
        self.logger.exception("IRubix handler failed: %s", error,
                              exc_info=(type(error), error, error.__traceback__))
        if self.callback is not None:
            result = self.callback(error, context)
            return await result if inspect.isawaitable(result) else result
        return None


class UniversalEventRouter:
    """Register and dispatch normalized events without binding to one platform."""

    def __init__(self):
        self._handlers: list[tuple[str | None, Callable, Callable | None]] = []

    def on(self, event_type: str | None = None, *, filter: Callable | None = None):
        def decorator(handler):
            self._handlers.append((event_type, handler, filter))
            return handler
        return decorator

    async def dispatch(self, event: Any):
        event_type = getattr(event, "type", None) or getattr(event, "update_type", None)
        results = []
        for expected, handler, predicate in tuple(self._handlers):
            if expected is not None and expected != event_type:
                continue
            if predicate is not None and not predicate(event):
                continue
            result = handler(event)
            results.append(await result if inspect.isawaitable(result) else result)
        return results


class KeyboardBuilder:
    """Build a neutral keyboard description; platform clients must translate it."""

    def __init__(self, *, inline: bool = False):
        self.inline = inline
        self.rows: list[list[dict[str, Any]]] = [[]]

    def button(self, text: str, *, callback_data: str | None = None,
               url: str | None = None):
        if not text:
            raise ValueError("Button text cannot be empty")
        if callback_data is not None and url is not None:
            raise ValueError("A button cannot have both callback_data and url")
        item = {"text": str(text)}
        if callback_data is not None:
            item["callback_data"] = str(callback_data)
        if url is not None:
            item["url"] = str(url)
        self.rows[-1].append(item)
        return self

    def new_row(self):
        if self.rows[-1]:
            self.rows.append([])
        return self

    def build(self):
        rows = [list(row) for row in self.rows if row]
        return {"inline": self.inline, "rows": rows}


class SessionManager:
    """Persist JSON-compatible user/chat sessions atomically on local disk."""

    def __init__(self, path: str | os.PathLike):
        self.path = Path(path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._sessions: dict[str, dict[str, Any]] = {}
        self.load()

    def load(self):
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            data = {}
        if not isinstance(data, dict):
            raise ValueError("Session file must contain a JSON object.")
        self._sessions = {
            str(key): dict(value) for key, value in data.items()
            if isinstance(value, dict)
        }
        return self

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_name(self.path.name + ".tmp")
        temporary.write_text(
            json.dumps(self._sessions, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary.replace(self.path)
        return self.path

    def create(self, session_id: Any, data: dict | None = None):
        key = str(session_id)
        self._sessions[key] = dict(data or {})
        self.save()
        return dict(self._sessions[key])

    def get(self, session_id: Any, key: str | None = None, default=None):
        session = self._sessions.get(str(session_id))
        if session is None:
            return default if key is not None else None
        return session.get(key, default) if key is not None else dict(session)

    def set(self, session_id: Any, key: str, value: Any):
        session = self._sessions.setdefault(str(session_id), {})
        session[key] = value
        self.save()
        return value

    def delete(self, session_id: Any):
        removed = self._sessions.pop(str(session_id), None)
        if removed is not None:
            self.save()
            return True
        return False

    def all(self):
        return {key: dict(value) for key, value in self._sessions.items()}


class UniversalClient:
    """A small registry/facade for already-created platform clients.

    Platform-specific method signatures remain platform-specific; this class
    deliberately does not pretend that every API supports identical features.
    """

    def __init__(self, **clients: Any):
        self.clients: dict[str, Any] = {}
        for platform, client in clients.items():
            self.add(platform, client)

    @staticmethod
    def _key(platform: str) -> str:
        return str(platform).strip().lower().replace("-", "_").replace(" ", "_")

    def add(self, platform: str, client: Any):
        key = self._key(platform)
        if not key or client is None:
            raise ValueError("A platform name and client are required.")
        if key in self.clients:
            raise ValueError(f"Client {key!r} is already registered.")
        self.clients[key] = client
        return client

    def get(self, platform: str):
        key = self._key(platform)
        try:
            return self.clients[key]
        except KeyError as exc:
            raise KeyError(f"No client registered for {key!r}.") from exc

    def remove(self, platform: str):
        return self.clients.pop(self._key(platform))

    def platforms(self):
        return tuple(self.clients)

    async def send_text(self, platform: str, chat_id: Any, text: str, **kwargs):
        client = self.get(platform)
        sender = getattr(client, "send_text", None) or getattr(client, "send_message", None)
        if sender is None:
            raise NotImplementedError(
                f"Client {self._key(platform)!r} has no text-send method."
            )
        result = sender(chat_id, text, **kwargs)
        return await result if inspect.isawaitable(result) else result

    async def broadcast_text(self, chat_targets: dict[str, Any], text: str, **kwargs):
        """Send text to {platform: chat_id}; return per-platform results."""
        results = {}
        for platform, chat_id in chat_targets.items():
            results[platform] = await self.send_text(platform, chat_id, text, **kwargs)
        return results


__all__ = [
    "PluginManager", "MiddlewareManager", "RateLimiter", "ConversationManager",
    "BotStats", "CommandPermissions", "MessageBuilder", "FileManager",
    "AIAdapter", "CloudStorageAdapter", "AutoReconnect", "WebhookAdapter",
    "DeveloperConsole", "SmartErrorHandler", "UniversalEventRouter", "KeyboardBuilder",
]
