"""Run multiple IRubix platform clients in one asyncio application."""
from __future__ import annotations

import asyncio
from importlib import import_module
from typing import Any

_PLATFORMS = {
    "rubika": (".bot", "IRubix"),
    "bale": (".bale.bot", "IRubix"),
    "soroush": (".soroush.bot", "IRubix"),
    "soroush_plus": (".soroush.bot", "IRubix"),
    "telegram": (".telegram.bot", "IRubix"),
}


class MultiBot:
    """Manage and run several IRubix bots concurrently."""

    def __init__(self):
        self.bots: dict[str, Any] = {}

    @staticmethod
    def _client_class(platform: str):
        key = str(platform).strip().lower().replace("-", "_").replace(" ", "_")
        target = _PLATFORMS.get(key)
        if target is None:
            choices = ", ".join(("rubika", "bale", "soroush", "telegram"))
            raise ValueError(f"Unsupported platform {platform!r}. Choose: {choices}.")
        module_path, class_name = target
        module = import_module(module_path, __package__)
        return getattr(module, class_name)

    def add(self, platform: str, token: str | None = None, *,
            name: str | None = None, **kwargs: Any):
        """Create, register, and return a platform bot."""
        client_name = name or str(platform).strip().lower().replace("-", "_").replace(" ", "_")
        if not client_name:
            raise ValueError("Bot name cannot be empty.")
        if client_name in self.bots:
            raise ValueError(f"A bot named {client_name!r} is already registered.")
        client_class = self._client_class(platform)
        client = client_class(token, **kwargs)
        self.bots[client_name] = client
        return client

    def get(self, name: str):
        """Return a registered bot by its name."""
        try:
            return self.bots[name]
        except KeyError as exc:
            raise KeyError(f"No bot named {name!r} is registered.") from exc

    def remove(self, name: str, *, stop: bool = True):
        """Remove a registered bot and optionally stop its polling loop."""
        client = self.get(name)
        if stop:
            client.stop()
        return self.bots.pop(name)

    def stop(self):
        """Ask every registered bot to stop."""
        for client in tuple(self.bots.values()):
            client.stop()

    async def start(self):
        """Run all registered bots concurrently until they stop."""
        if not self.bots:
            raise RuntimeError("No bots registered. Add a bot before calling start().")
        tasks = [
            asyncio.create_task(client.start(), name=f"irubix:{name}")
            for name, client in self.bots.items()
        ]
        try:
            await asyncio.gather(*tasks)
        finally:
            self.stop()
            for task in tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)

    def run(self):
        """Start all bots; return a coroutine inside an active event loop."""
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            try:
                asyncio.run(self.start())
            except KeyboardInterrupt:
                self.stop()
            return None
        return self.start()

    def __len__(self):
        return len(self.bots)

    def __iter__(self):
        return iter(self.bots.items())


__all__ = ["MultiBot"]
