"""Composable filters for Rubika bot events."""
from __future__ import annotations
from typing import Callable

class Filter:
    def __init__(self, predicate: Callable):
        self.predicate = predicate
    def __call__(self, event):
        return bool(self.predicate(event))
    def __and__(self, other):
        return Filter(lambda event: self(event) and other(event))
    def __or__(self, other):
        return Filter(lambda event: self(event) or other(event))
    def __invert__(self):
        return Filter(lambda event: not self(event))

def Text(value: str | None = None):
    return Filter(lambda e: bool(e.text) and (value is None or value in e.text))
def ChatTypeFilter(value: str):
    return Filter(lambda e: (e.message.get("chat") or {}).get("chat_type") == value)
def FromUser(user_id: str):
    return Filter(lambda e: str(e.sender_id) == str(user_id))
def IsImage():
    return Filter(lambda e: str(((e.message.get("file") or {}).get("file_type") or "")).lower() == "image")
def IsVideo():
    return Filter(lambda e: str(((e.message.get("file") or {}).get("file_type") or "")).lower() == "video")
def IsVoice():
    return Filter(lambda e: str(((e.message.get("file") or {}).get("file_type") or "")).lower() == "voice")
def Command(name: str | None = None):
    return Filter(lambda e: bool(e.command) and (name is None or e.command == name.lstrip("/")))
