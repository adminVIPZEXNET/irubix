"""Shared helpers for Telegram-compatible Bot API clients.

The clients intentionally keep platform-specific HTTP and response handling,
while this module provides generic endpoint dispatch and multipart encoding.
"""
from __future__ import annotations

import mimetypes
import uuid
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import quote


def encode_request_payload(payload: dict[str, Any]):
    """Return (body, content_type), using multipart for Path/bytes file values."""
    files: dict[str, tuple[str, bytes, str]] = {}
    for key, value in payload.items():
        if isinstance(value, Path):
            data = value.read_bytes()
            filename = value.name
            mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
            files[key] = (filename, data, mime)
        elif isinstance(value, bytes):
            files[key] = (f"{key}.bin", value, "application/octet-stream")
        elif isinstance(value, tuple) and len(value) == 2 and isinstance(value[1], bytes):
            filename, data = value
            filename = str(filename)
            mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
            files[key] = (filename, data, mime)

    if not files:
        import json
        return json.dumps(payload or {}, ensure_ascii=False).encode("utf-8"), "application/json"

    boundary = "----Ertebat" + uuid.uuid4().hex
    chunks: list[bytes] = []
    for key, value in payload.items():
        chunks.append(f"--{boundary}\r\n".encode("ascii"))
        if key in files:
            filename, data, mime = files[key]
            safe_name = filename.replace('"', "")
            chunks.append(
                (
                    f'Content-Disposition: form-data; name="{key}"; filename="{safe_name}"\r\n'
                    f"Content-Type: {mime}\r\n\r\n"
                ).encode("utf-8")
            )
            chunks.extend((data, b"\r\n"))
        else:
            import json
            if isinstance(value, (dict, list, tuple)):
                field_value = json.dumps(value, ensure_ascii=False)
            elif isinstance(value, bool):
                field_value = "true" if value else "false"
            elif value is None:
                field_value = ""
            else:
                field_value = str(value)
            chunks.extend((
                f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode("utf-8"),
                field_value.encode("utf-8"),
                b"\r\n",
            ))
    chunks.append(f"--{boundary}--\r\n".encode("ascii"))
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


class BotAPIMethods:
    """Generic access to platform Bot API endpoints.

    Every endpoint can be called by snake_case or native camelCase name.
    Parameters are passed as keyword arguments; use call_api for exact names.
    """

    async def call_api(self, method: str, **params: Any):
        """Call any endpoint supported by the selected messaging platform."""
        if not isinstance(method, str) or not method or "/" in method:
            raise ValueError("method must be a non-empty API method name.")
        return await self.request(method, params or None)

    _POSITIONAL_PARAMETERS = {
        "getMe": (),
        "getChat": ("chat_id",),
        "getChatMember": ("chat_id", "user_id"),
        "getFile": ("file_id",),
        "sendMessage": ("chat_id", "text"),
        "sendPhoto": ("chat_id", "photo"),
        "sendAudio": ("chat_id", "audio"),
        "sendDocument": ("chat_id", "document"),
        "sendVideo": ("chat_id", "video"),
        "sendAnimation": ("chat_id", "animation"),
        "sendVoice": ("chat_id", "voice"),
        "sendVideoNote": ("chat_id", "video_note"),
        "sendSticker": ("chat_id", "sticker"),
        "sendLocation": ("chat_id", "latitude", "longitude"),
        "sendContact": ("chat_id", "phone_number", "first_name"),
        "sendPoll": ("chat_id", "question", "options"),
        "sendChatAction": ("chat_id", "action"),
        "forwardMessage": ("chat_id", "from_chat_id", "message_id"),
        "copyMessage": ("chat_id", "from_chat_id", "message_id"),
        "editMessageText": ("chat_id", "message_id", "text"),
        "deleteMessage": ("chat_id", "message_id"),
        "answerCallbackQuery": ("callback_query_id",),
        "setWebhook": ("url",),
        "setMyCommands": ("commands",),
    }

    def __getattr__(self, name: str):
        # Resolve otherwise-unimplemented API methods dynamically. This keeps
        # the SDK forward-compatible with new endpoints without pretending the
        # remote platform supports endpoints it has not implemented.
        if not name or name.startswith("_"):
            raise AttributeError(name)
        endpoint = name.split("_")[0] + "".join(
            part[:1].upper() + part[1:] for part in name.split("_")[1:]
        )

        async def invoke(*args: Any, **kwargs: Any):
            if args:
                parameter_names = self._POSITIONAL_PARAMETERS.get(endpoint)
                if parameter_names is None or len(args) > len(parameter_names):
                    raise TypeError(
                        f"{name}() accepts keyword arguments for this endpoint; "
                        "use call_api(method, **params) for full API access."
                    )
                for key, value in zip(parameter_names, args):
                    if key in kwargs:
                        raise TypeError(f"{name}() got multiple values for {key!r}.")
                    kwargs[key] = value
            return await self.request(endpoint, kwargs or None)

        invoke.__name__ = name
        invoke.__doc__ = f"Call the {endpoint} endpoint using keyword parameters."
        return invoke

    async def download_file(self, file_id: str, destination: str | Path | None = None):
        """Download a file by ID; return bytes or save it and return its Path."""
        info = await self.request("getFile", {"file_id": file_id})
        if not isinstance(info, dict):
            raise RuntimeError("The platform did not return file metadata.")
        file_path = info.get("file_path") or info.get("path")
        direct_url = info.get("download_url") or info.get("file_url") or info.get("url")
        if direct_url:
            url = direct_url
        elif file_path:
            base = getattr(self, "FILE_URL", "").rstrip("/")
            if not base:
                base = getattr(self, "base_url", "").rstrip("/") + "/file"
            url = f"{base}/bot{self.token}/{quote(str(file_path), safe='/')}"
        else:
            raise RuntimeError("File metadata does not contain a downloadable path or URL.")

        def fetch():
            request = urllib.request.Request(url, headers={"User-Agent": "Ertebat/0.13"})
            with urllib.request.urlopen(request, timeout=getattr(self, "timeout", 40)) as response:
                return response.read()

        data = await asyncio.to_thread(fetch)
        if destination is None:
            return data
        target = Path(destination)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return target
