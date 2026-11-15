"""Shared terminal helpers for IRubix."""
from __future__ import annotations

import getpass
import sys


def resolve_token(token: str | None, platform: str) -> str:
    """Return a supplied token or securely request one from the terminal."""
    if isinstance(token, str) and token.strip():
        return token.strip()

    prompt = f"[IRubix:{platform}] Bot token is missing.\n[IRubix:{platform}] Enter your bot token: "
    if not sys.stdin or not sys.stdin.isatty():
        raise ValueError(
            f"{platform} bot token is missing. Pass it to the constructor "
            f'or run the program in an interactive terminal.'
        )

    try:
        entered = getpass.getpass(prompt)
    except (EOFError, OSError) as exc:
        raise RuntimeError(
            f"Could not read the {platform} bot token securely from this terminal."
        ) from exc

    if not entered or not entered.strip():
        raise ValueError(f"{platform} bot token cannot be empty.")

    return entered.strip()
