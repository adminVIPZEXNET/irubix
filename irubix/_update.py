"""GitHub update notifications for IRubix, with Android-friendly TLS handling."""
from __future__ import annotations

import os
import re
import ssl
import sys
import threading
from urllib.error import URLError
from urllib.request import Request, urlopen

_GITHUB_VERSION = "https://raw.githubusercontent.com/adminVIPZEXNET/irubix/main/irubix/__init__.py"
_TIMEOUT = 8.0

_CYAN = "\033[96m"
_GREEN = "\033[92m"
_RED = "\033[91m"
_YELLOW = "\033[93m"
_MAGENTA = "\033[95m"
_BOLD = "\033[1m"
_RESET = "\033[0m"


def _color(text: str, color: str) -> str:
    if os.environ.get("NO_COLOR") is not None or os.environ.get("TERM", "").lower() == "dumb":
        return text
    return f"{color}{text}{_RESET}"


def _version_key(version: str) -> tuple[int, ...]:
    parts = tuple(int(part) for part in re.findall(r"\d+", str(version)))
    return parts or (0,)


def _is_newer(latest: str, installed: str) -> bool:
    return _version_key(latest) > _version_key(installed)


def _read_source(context=None) -> str:
    request = Request(
        _GITHUB_VERSION,
        headers={"Accept": "text/plain", "User-Agent": "IRubix-update-check"},
    )
    with urlopen(request, timeout=_TIMEOUT, context=context) as response:
        return response.read().decode("utf-8")


def _latest_github_version() -> str:
    try:
        source = _read_source()
    except (URLError, ssl.SSLError, OSError):
        # Some Android Python distributions do not configure a usable CA
        # bundle. Use certifi when installed; never disable TLS verification.
        try:
            import certifi
        except ImportError:
            raise
        source = _read_source(ssl.create_default_context(cafile=certifi.where()))

    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', source, re.MULTILINE)
    if not match:
        raise ValueError("Could not read IRubix version from GitHub")
    return match.group(1)


def _check(installed: str) -> None:
    try:
        latest = _latest_github_version()
        if _is_newer(latest, installed):
            lines = [
                "",
                _color("[IRubix] A new version is available!", _BOLD + _CYAN),
                _color(f"Current version: {installed}", _YELLOW),
                _color(f"Latest version: {latest}", _GREEN),
                "",
                _color("To update from GitHub, run:", _MAGENTA),
                _color(
                    "python -m pip install --upgrade --no-cache-dir --no-build-isolation "
                    "https://github.com/adminVIPZEXNET/irubix/archive/refs/heads/main.zip",
                    _BOLD,
                ),
                "",
            ]
            print("\n".join(lines), file=sys.stderr, flush=True)
        elif _version_key(latest) == _version_key(installed):
            print(_color(f"[IRubix] You are using the latest version ({installed}).", _GREEN), flush=True)
    except Exception as exc:
        print(
            _color(f"[IRubix] Update check failed: {type(exc).__name__}: {exc}", _RED),
            file=sys.stderr,
            flush=True,
        )


def check_for_updates(installed_version: str) -> None:
    """Check GitHub during import and finish before client token prompts."""
    if os.environ.get("IRUBIX_DISABLE_UPDATE_CHECK", "").lower() in {
        "1", "true", "yes", "on"
    }:
        return
    thread = threading.Thread(
        target=_check,
        args=(installed_version,),
        name="irubix-update-check",
        daemon=True,
    )
    thread.start()
    # Keep startup bounded, but ensure the result appears before bot.run()
    # or a hidden token prompt can take over the terminal.
    thread.join(timeout=_TIMEOUT + 2)
