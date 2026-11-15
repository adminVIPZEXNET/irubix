"""IRubix: lightweight Python clients for messaging platforms.

Platform modules are imported only when requested.
"""
from .bot import IRubix, Bot, Event, RubikaAPIError

__author__ = "mahdishami"
__version__ = "0.9.0"
from ._update import check_for_updates
check_for_updates(__version__)

__all__ = [
    "IRubix", "Bot", "Event", "RubikaAPIError",
    "bale", "soroush", "telegram", "__version__", "__author__",
]


def __getattr__(name):
    """Load platform modules on first access."""
    if name in {"bale", "soroush", "telegram"}:
        from importlib import import_module
        module = import_module(f".{name}", __name__)
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(set(globals()) | set(__all__))
