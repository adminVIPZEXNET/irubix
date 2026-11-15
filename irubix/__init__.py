"""IRubix: lightweight async clients and platform-neutral bot utilities."""
from importlib import import_module
from types import ModuleType

from .bot import Bot, Event, IRubix as _RubikaClient, RubikaAPIError
from .multibot import MultiBot
from .features import (
    AIAdapter, AutoReconnect, BotStats, CloudStorageAdapter,
    CommandPermissions, ConversationManager, DeveloperConsole, FileManager,
    MessageBuilder, MiddlewareManager, PluginManager, RateLimiter,
    SmartErrorHandler, WebhookAdapter, UniversalEventRouter, KeyboardBuilder,
    SessionManager, UniversalClient,
)

__author__ = "mahdishami"
__version__ = "0.10.0"

from ._update import check_for_updates
check_for_updates(__version__)

__all__ = [
    "Rubika", "Bot", "Event", "RubikaAPIError",
    "rubika", "bale", "soroush", "telegram",
    "__version__", "__author__", "MultiBot",
    "PluginManager", "MiddlewareManager", "RateLimiter",
    "ConversationManager", "BotStats", "CommandPermissions",
    "MessageBuilder", "FileManager", "AIAdapter", "CloudStorageAdapter",
    "AutoReconnect", "WebhookAdapter", "DeveloperConsole", "SmartErrorHandler",
    "UniversalEventRouter", "KeyboardBuilder", "SessionManager", "UniversalClient",
]

_PLATFORM_MODULES = {
    "rubika": ".bot",
    "bale": ".bale",
    "soroush": ".soroush",
    "telegram": ".telegram",
}


class _CallablePlatformModule(ModuleType):
    """Allow a platform namespace to be called directly with its bot token."""

    def __call__(self, *args, **kwargs):
        return self.IRubix(*args, **kwargs)


class Rubika(_RubikaClient):
    """Create a Rubika bot directly: Rubika("TOKEN")."""

    IRubix = _RubikaClient
    Bot = _RubikaClient
    Event = Event
    RubikaAPIError = RubikaAPIError
    APIError = RubikaAPIError


def __getattr__(name):
    """Load a platform namespace only when it is requested."""
    module_path = _PLATFORM_MODULES.get(name)
    if module_path is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = import_module(module_path, __name__)
    module.__class__ = _CallablePlatformModule
    globals()[name] = module
    return module


def __dir__():
    return sorted(set(globals()) | set(__all__))
