"""Non-blocking GitHub update notifications for IRubix."""
from __future__ import annotations

import os
import re
import sys
import threading
from urllib.request import Request, urlopen

_GITHUB_VERSION = "https://raw.githubusercontent.com/adminVIPZEXNET/irubix/main/irubix/__init__.py"
_TIMEOUT = 5.0

# ANSI colors are supported by modern terminals, including Pydroid.
_CYAN = "\033[96m"
_GREEN = "\033[92m"
_YELLOW = "\033[93m"
_MAGENTA = "\033[95m"
_BOLD = "\033[1m"
_RESET = "\033[0m"


def _color(text: str, color: str) -> str:
    """Apply terminal color unless the user explicitly disables colors."""
    if os.environ.get("NO_COLOR") is not None or os.environ.get("TERM", "").lower() == "dumb":
        return text
    return f"{color}{text}{_RESET}"


def _version_key(version: str) -> tuple[int, ...]:
    """Compare ordinary numeric release versions without extra dependencies."""
    parts = tuple(int(part) for part in re.findall(r"\d+", str(version)))
    return parts or (0,)


def _is_newer(latest: str, installed: str) -> bool:
    return _version_key(latest) > _version_key(installed)


def _latest_github_version() -> str:
    request = Request(
        _GITHUB_VERSION,
        headers={"Accept": "text/plain", "User-Agent": "IRubix-update-check"},
    )
    with urlopen(request, timeout=_TIMEOUT) as response:
        source = response.read().decode("utf-8")
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', source, re.MULTILINE)
    if not match:
        raise ValueError("Could not read IRubix version from GitHub")
    return match.group(1)


def _check(installed: str) -> None:
    """Print a colored English upgrade notice when GitHub has a newer release."""
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
    except Exception:
        # Update checks must never interrupt or slow down the user's program.
        return


def check_for_updates(installed_version: str) -> None:
    """Check GitHub in a daemon thread; never block application startup."""
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
