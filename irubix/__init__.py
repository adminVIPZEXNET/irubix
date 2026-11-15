"""IRubix: lightweight async clients for supported messaging platforms."""
from importlib import import_module
from types import ModuleType

from .bot import Bot, Event, IRubix as _RubikaClient, RubikaAPIError
from .multibot import MultiBot
from .filters import Filter, Text, ChatTypeFilter, FromUser, IsImage, IsVideo, IsVoice, Command
from .models import (APIModel, AuxData, Bot as BotModel, BotCommand, ButtonType, Chat, ChatKeypadType, ChatType, ContactMessage, File, FileType, ForwardedFrom, InlineMessage, Keypad, KeypadRow, Location, Message, Metadata, MetadataPart, Poll, PollStatus, Update, UpdateType)
__author__ = "mahdishami"
__version__ = "0.12.0"

from ._update import check_for_updates
check_for_updates(__version__)

__all__ = [
    "Rubika", "Bot", "Event", "RubikaAPIError", "Filter", "Text", "ChatTypeFilter", "FromUser", "IsImage", "IsVideo", "IsVoice", "Command",
    "rubika", "bale", "soroush", "telegram",
    "__version__", "__author__", "MultiBot", "APIModel", "File", "Chat",
    "AuxData", "Location", "BotModel", "BotCommand", "ForwardedFrom",
    "ContactMessage", "PollStatus", "Poll", "Message", "Update",
    "InlineMessage", "MetadataPart", "Metadata", "KeypadRow", "Keypad",
    "ChatType", "FileType", "ChatKeypadType", "UpdateType", "ButtonType",
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
