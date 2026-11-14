"""IRubix: lightweight Python clients for Iranian messaging platforms.

Optional platform modules are imported only when requested.
"""
from .bot import IRubix, Bot, Event, RubikaAPIError

__author__ = "mahdishami"
__version__ = "0.8.1"
from ._update import check_for_updates
check_for_updates(__version__)

__all__ = [
    "IRubix", "Bot", "Event", "RubikaAPIError",
    "bale", "soroush", "shad", "__version__", "__author__",
]


def __getattr__(name):
    """Load optional platform modules on first access."""
    if name in {"bale", "soroush", "shad"}:
        from importlib import import_module
        module = import_module(f".{name}", __name__)
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(set(globals()) | set(__all__))
