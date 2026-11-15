"""IRubix: lightweight async clients for messaging platforms."""

from importlib import import_module

from .bot import Bot, Event, IRubix, RubikaAPIError

__author__ = "mahdishami"
__version__ = "0.9.0"

from ._update import check_for_updates

check_for_updates(__version__)

__all__ = [
    "IRubix",
    "Bot",
    "Event",
    "RubikaAPIError",
    "rubika",
    "bale",
    "soroush",
    "telegram",
    "__version__",
    "__author__",
]

_PLATFORM_MODULES = {
    "rubika": ".bot",
    "bale": ".bale",
    "soroush": ".soroush",
    "telegram": ".telegram",
}


def __getattr__(name):
    """Import a platform client only when it is requested."""
    module_path = _PLATFORM_MODULES.get(name)
    if module_path is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module = import_module(module_path, __name__)
    globals()[name] = module
    return module


def __dir__():
    return sorted(set(globals()) | set(__all__))
