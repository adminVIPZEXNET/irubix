"""Shared terminal helpers for IRubix."""
from __future__ import annotations

import os
import sys


_GREEN = "\033[92m"
_CYAN = "\033[96m"
_RESET = "\033[0m"


def _color(value: str, code: str) -> str:
    if os.environ.get("NO_COLOR") is not None or os.environ.get("TERM", "").lower() == "dumb":
        return value
    return f"{code}{value}{_RESET}"


def _read_masked(prompt: str) -> str:
    """Read terminal input while displaying one green asterisk per character."""
    sys.stdout.write(_color(prompt, _CYAN))
    sys.stdout.flush()
    chars: list[str] = []

    if os.name == "nt":
        import msvcrt

        while True:
            char = msvcrt.getwch()
            if char in ("\r", "\n"):
                sys.stdout.write("\n")
                break
            if char == "\003":
                raise KeyboardInterrupt
            if char in ("\b", "\x7f"):
                if chars:
                    chars.pop()
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
                continue
            if char == "\x00":
                msvcrt.getwch()
                continue
            if char.isprintable():
                chars.append(char)
                sys.stdout.write(_color("*", _GREEN))
                sys.stdout.flush()
        return "".join(chars)

    import termios
    import tty

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while True:
            char = sys.stdin.read(1)
            if char in ("\r", "\n"):
                sys.stdout.write("\n")
                sys.stdout.flush()
                break
            if char in ("\x03",):
                raise KeyboardInterrupt
            if char in ("\x04",):
                sys.stdout.write("\n")
                sys.stdout.flush()
                break
            if char in ("\x7f", "\b"):
                if chars:
                    chars.pop()
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
                continue
            if char.isprintable():
                chars.append(char)
                sys.stdout.write(_color("*", _GREEN))
                sys.stdout.flush()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return "".join(chars)


def resolve_token(token: str | None, platform: str) -> str:
    """Return a supplied token or securely request one from the terminal."""
    if isinstance(token, str) and token.strip():
        return token.strip()

    if not sys.stdin or not sys.stdin.isatty():
        raise ValueError(
            f"{platform} bot token is missing. Pass it to the constructor "
            "or run the program in an interactive terminal."
        )

    prompt = (
        f"[IRubix:{platform}] Bot token is missing.\n"
        f"[IRubix:{platform}] Enter your bot token: "
    )
    try:
        entered = _read_masked(prompt)
    except (EOFError, OSError, AttributeError) as exc:
        raise RuntimeError(
            f"Could not read the {platform} bot token from this terminal."
        ) from exc

    if not entered or not entered.strip():
        raise ValueError(f"{platform} bot token cannot be empty.")

    return entered.strip()
