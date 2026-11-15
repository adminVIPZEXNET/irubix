"""Convenience methods for the documented Rubika Bot API."""
from __future__ import annotations

from typing import Any


class RubikaAPIMethods:
    """Mixin implementing documented Rubika Bot API endpoints."""

    async def get_updates(self, offset_id: str | None = None, limit: int = 100):
        """Fetch updates; pass next_offset_id as offset_id on the next call."""
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100.")
        payload: dict[str, Any] = {"limit": limit}
        if offset_id is not None:
            payload["offset_id"] = offset_id
        return await self.request("getUpdates", payload)

    async def send_location(
        self, chat_id: str, latitude: str | float, longitude: str | float,
        **kwargs: Any,
    ):
        """Send a geographic location to a chat."""
        payload = {"chat_id": chat_id, "latitude": str(latitude),
                   "longitude": str(longitude)}
        payload.update(self._rubika_optional(kwargs, {
            "chat_keypad", "inline_keypad", "disable_notification",
            "reply_to_message_id", "chat_keypad_type",
        }))
        return await self.request("sendLocation", payload)

    async def send_contact(
        self, chat_id: str, first_name: str, phone_number: str,
        last_name: str | None = None, **kwargs: Any,
    ):
        """Send a contact card to a chat."""
        payload = {"chat_id": chat_id, "first_name": first_name,
                   "phone_number": phone_number}
        if last_name is not None:
            payload["last_name"] = last_name
        payload.update(self._rubika_optional(kwargs, {
            "chat_keypad", "inline_keypad", "disable_notification",
            "reply_to_message_id", "chat_keypad_type",
        }))
        return await self.request("sendContact", payload)

    async def edit_inline_keypad(
        self, chat_id: str, message_id: str, inline_keypad: dict,
    ):
        """Replace an existing message's inline keypad.

        Rubika's documentation prose names editMessageKeypad, while its
        request example uses editInlineKeypad. The example endpoint is used.
        """
        return await self.request("editInlineKeypad", {
            "chat_id": chat_id, "message_id": message_id,
            "inline_keypad": inline_keypad,
        })

    async def edit_message_keypad(
        self, chat_id: str, message_id: str, inline_keypad: dict,
    ):
        """Alias for edit_inline_keypad."""
        return await self.edit_inline_keypad(chat_id, message_id, inline_keypad)

    async def edit_chat_keypad(
        self, chat_id: str, chat_keypad: dict | None = None,
        chat_keypad_type: str = "New",
    ):
        """Set or remove a chat keypad (use chat_keypad_type='Remove')."""
        if chat_keypad_type not in {"New", "Remove", "None"}:
            raise ValueError("chat_keypad_type must be New, Remove or None.")
        payload: dict[str, Any] = {
            "chat_id": chat_id, "chat_keypad_type": chat_keypad_type,
        }
        if chat_keypad is not None:
            payload["chat_keypad"] = chat_keypad
        if chat_keypad_type == "New" and chat_keypad is None:
            raise ValueError("chat_keypad is required when chat_keypad_type='New'.")
        return await self.request("editChatKeypad", payload)

    async def set_commands(self, bot_commands: list[dict[str, str]]):
        """Register the bot's slash commands."""
        if not isinstance(bot_commands, list):
            raise TypeError("bot_commands must be a list of command dictionaries.")
        return await self.request("setCommands", {"bot_commands": bot_commands})

    async def update_bot_endpoints(self, url: str, endpoint_type: str):
        """Configure a webhook endpoint; the URL must be public HTTPS."""
        if not url.startswith("https://"):
            raise ValueError("Rubika webhook endpoints must use HTTPS.")
        allowed = {
            "ReceiveUpdate", "ReceiveInlineMessage", "ReceiveQuery",
            "GetSelectionItem", "SearchSelectionItems",
        }
        if endpoint_type not in allowed:
            raise ValueError(f"type must be one of: {', '.join(sorted(allowed))}")
        return await self.request("updateBotEndpoints", {
            "url": url, "type": endpoint_type,
        })

    async def update_bot_endpoint(self, url: str, endpoint_type: str):
        """Singular-name alias for update_bot_endpoints."""
        return await self.update_bot_endpoints(url, endpoint_type)

    async def request_send_file(self, file_type: str = "File"):
        """Request an upload URL for File, Image, Voice, Video, Music or Gif."""
        allowed = {"File", "Image", "Voice", "Video", "Music", "Gif"}
        if file_type not in allowed:
            raise ValueError(f"type must be one of: {', '.join(sorted(allowed))}")
        return await self.request("requestSendFile", {"type": file_type})

    async def send_file_id(
        self, chat_id: str, file_id: str, text: str | None = None,
        **kwargs: Any,
    ):
        """Send an already-uploaded Rubika file by its file_id."""
        payload: dict[str, Any] = {"chat_id": chat_id, "file_id": file_id}
        if text is not None:
            payload["text"] = text
        payload.update(self._rubika_optional(kwargs, {
            "reply_to_message_id", "disable_notification", "chat_keypad",
            "inline_keypad", "chat_keypad_type",
        }))
        return await self.request("sendFile", payload)

    @staticmethod
    def _rubika_optional(values: dict, allowed: set[str]) -> dict:
        """Filter optional fields and omit None values."""
        return {key: value for key, value in values.items()
                if key in allowed and value is not None}
