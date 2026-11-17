# Multi-platform Bot API methods

Ertebat exposes a common asynchronous interface for Rubika, Bale, Soroush Plus,
and Telegram. The platform clients remain independent: an endpoint is executed
by the selected platform's server, so a method name being callable does not
mean that every platform implements that endpoint.

## Generic access to API endpoints

All three clients (Bale, Soroush Plus, Telegram) provide dynamic API access.
Snake-case names are converted to the native endpoint name:

```python
from ertebat import telegram

bot = telegram("TELEGRAM_TOKEN")

# Named Python method -> sendVideo
await bot.send_video(chat_id=123456, video="FILE_ID", caption="Demo")

# Native API endpoint name
await bot.call_api("sendSharedWidget", chat_id=123456, widget_id="widget-id")

# Other endpoints can be used the same way
await bot.send_media_group(chat_id=123456, media=[...])
await bot.set_chat_menu_button(chat_id=123456, menu_button={...})
```

Dynamic methods accept endpoint parameters as keyword arguments. Common
endpoints also accept positional arguments in their conventional order.
For endpoints not covered by a convenience method, use `call_api()`.

## Common Bot API method families

Depending on platform support, the following endpoint families can be called
using snake_case names:

- Identity and updates: `get_me`, `get_updates`, `log_out`, `close`
- Webhooks: `set_webhook`, `delete_webhook`, `get_webhook_info`
- Messages: `send_message`, `forward_message`, `copy_message`,
  `edit_message_text`, `edit_message_caption`, `edit_message_media`,
  `edit_message_reply_markup`, `delete_message`
- Media: `send_photo`, `send_audio`, `send_document`, `send_video`,
  `send_animation`, `send_voice`, `send_video_note`, `send_sticker`,
  `send_media_group`
- Other message types: `send_location`, `send_contact`, `send_poll`,
  `send_chat_action`
- Files: `get_file`, `download_file`
- Callbacks and commands: `answer_callback_query`, `set_my_commands`,
  `get_my_commands`, `delete_my_commands`
- Chat administration: `get_chat`, `get_chat_member`,
  `get_chat_administrators`, `ban_chat_member`, `unban_chat_member`,
  `restrict_chat_member`, `promote_chat_member`, `pin_chat_message`,
  `unpin_chat_message`, `leave_chat`

Telegram's official Bot API contains additional and newer endpoints. They can
also be invoked through the dynamic interface without waiting for a dedicated
wrapper, for example `bot.send_widget(...)` or
`bot.call_api("sendWidget", ...)`. Telegram's server remains the source of
truth for the current endpoint and parameter schema.

## Soroush Plus

The documented Soroush Plus Bot API method set includes:

`get_me`, `send_message`, `forward_message`, `copy_message`,
`send_photo`, `send_audio`, `send_document`, `send_video`,
`send_animation`, `send_voice`, `send_video_note`, `send_media_group`,
`send_location`, `send_contact`, `send_sticker`, `send_chat_action`,
`get_file`, `download_file`, `answer_callback_query`,
`set_my_commands`, `get_my_commands`, `delete_my_commands`,
`edit_message_text`, `edit_message_caption`, `edit_message_media`,
`edit_message_reply_markup`, `delete_message`, `get_updates`,
`set_webhook`, `delete_webhook`, and `get_webhook_info`.

## Bale

Bale's Bot API is Telegram-Bot-API-like, but support and parameter availability
must be checked against Bale's own documentation and server response. Ertebat
lets you call endpoint names directly; unsupported endpoints are returned as
Bale API errors rather than being simulated locally.

## Upload and download files

Pass a `pathlib.Path`, `bytes`, or a `(filename, bytes)` pair for a file
parameter. Ertebat automatically switches the request to multipart form data.

```python
from pathlib import Path
from ertebat import telegram

bot = telegram("TELEGRAM_TOKEN")

await bot.send_photo(123456, Path("photo.jpg"), caption="Local file")
await bot.send_document(123456, Path("report.pdf"))

# Return file bytes:
data = await bot.download_file("FILE_ID")

# Or save it and receive the destination Path:
saved = await bot.download_file("FILE_ID", "downloads/photo.jpg")
```

A string file value is treated as a file ID or URL according to the platform's
API; use `Path` when you want to upload a local file.
