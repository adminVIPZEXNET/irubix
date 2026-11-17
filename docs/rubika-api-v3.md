# Rubika Bot API v3 — Ertebat

The Rubika client exposes the documented API through asynchronous Python methods.
The direct constructor remains:

```python
from ertebat import Rubika

bot = Rubika("YOUR_BOT_TOKEN")
```

## Complete endpoint coverage

| Rubika endpoint | Ertebat method |
|---|---|
| `getMe` | `get_me()` |
| `sendMessage` | `send_message(chat_id, text, **kwargs)`, `send_text(...)` |
| `sendPoll` | `send_poll(chat_id, question, options)` |
| `sendLocation` | `send_location(chat_id, latitude, longitude, **kwargs)` |
| `sendContact` | `send_contact(chat_id, first_name, phone_number, last_name=None, **kwargs)` |
| `getChat` | `get_chat(chat_id)` |
| `getUpdates` | `get_updates(offset_id=None, limit=100)` |
| `forwardMessage` | `forward_message(from_chat_id, message_id, to_chat_id, disable_notification=False)` |
| `editMessageText` | `edit_message_text(chat_id, message_id, text)` |
| `editInlineKeypad` | `edit_inline_keypad(chat_id, message_id, inline_keypad)` |
| `deleteMessage` | `delete_message(chat_id, message_id)` |
| `setCommands` | `set_commands(bot_commands)` |
| `updateBotEndpoints` | `update_bot_endpoints(url, endpoint_type)` |
| `editChatKeypad` | `edit_chat_keypad(chat_id, chat_keypad=None, chat_keypad_type="New")` |
| `getFile` | `get_file(file_id)` |
| `requestSendFile` | `request_send_file(file_type="File")` |
| `sendFile` | `send_file_id(chat_id, file_id, text=None, **kwargs)`; `send_file(...)` uploads a local file first |
| `banChatMember` | `ban_chat_member(chat_id, user_id)` |
| `unbanChatMember` | `unban_chat_member(chat_id, user_id)` |

All methods are `async` and use the existing `await` convention. The low-level
`request(method, input)` remains available for newly released endpoints.

## Examples

### Send a location and contact

```python
await bot.send_location(CHAT_ID, 35.6892, 51.3890)
await bot.send_contact(
    CHAT_ID,
    first_name="Ada",
    last_name="Lovelace",
    phone_number="+10000000000",
)
```

### Poll updates manually

```python
result = await bot.get_updates(limit=50)
data = result.get("data") or result
for update in data.get("updates", []):
    print(update.get("type"), update.get("chat_id"))
next_offset = data.get("next_offset_id")
```

### Configure webhooks

Rubika requires a publicly reachable HTTPS endpoint. The endpoint type must be
one of `ReceiveUpdate`, `ReceiveInlineMessage`, `ReceiveQuery`,
`GetSelectionItem`, or `SearchSelectionItems`.

```python
await bot.update_bot_endpoints(
    "https://example.com/rubika/update",
    "ReceiveUpdate",
)
await bot.update_bot_endpoints(
    "https://example.com/rubika/inline",
    "ReceiveInlineMessage",
)
```

### Handle webhook payloads

Your HTTPS route can pass the parsed JSON body directly to the client. Both the `{"update": ...}` and `{"inline_message": ...}` envelopes are normalized before registered handlers run.

```python
@app.post("/rubika/update")  # example route in your web framework
async def rubika_update(request):
    await bot.process_webhook(await request.json())
    return {"ok": True}
```

### Manage chat keyboards

```python
keypad = {
    "rows": [{"buttons": [
        {"id": "help", "type": "Simple", "button_text": "Help"},
    ]}],
    "resize_keyboard": True,
    "one_time_keyboard": False,
}
await bot.edit_chat_keypad(CHAT_ID, keypad, "New")
await bot.edit_chat_keypad(CHAT_ID, chat_keypad_type="Remove")
```

### Set commands and edit an inline keypad

```python
await bot.set_commands([
    {"command": "start", "description": "Start the bot"},
    {"command": "help", "description": "Show help"},
])
await bot.edit_inline_keypad(CHAT_ID, MESSAGE_ID, keypad)
```

## Models

The package exports lightweight data models from `ertebat.models` and the package
root: `File`, `Chat`, `BotModel`, `BotCommand`, `Message`, `Update`,
`InlineMessage`, `Location`, `AuxData`, `Poll`, `PollStatus`,
`ForwardedFrom`, `ContactMessage`, `Metadata`, `MetadataPart`,
`Keypad`, and `KeypadRow`. Enum-like constants include `ChatType`,
`FileType`, `ChatKeypadType`, `UpdateType`, and `ButtonType`.

```python
from ertebat import Chat, File, Message, Update, FileType

chat = Chat.from_dict({"chat_id": "CHAT_ID", "chat_type": "Group"})
print(chat.chat_id, FileType.IMAGE)

message = Message.from_dict({"message_id": "123", "text": "Hello"})
update = Update.from_dict({"type": "NewMessage", "new_message": message.to_dict()})
```

## Documentation notes

- Rubika's prose calls the inline-keypad endpoint `editMessageKeypad`, but its
  own cURL example calls `editInlineKeypad`. Ertebat uses the example's endpoint.
- The endpoint update method is named `updateBotEndpoints` in the supplied
  documentation; the client uses that exact spelling.
- `send_file()` is the convenience upload workflow; `send_file_id()` sends a
  file that has already been uploaded.
- The raw response dictionaries are preserved as returned by Rubika. Model
  classes are optional helpers and do not alter API responses.

## Extended convenience API

Media wrappers use the existing documented two-step upload flow:
`send_image`, `send_video`, `send_voice`, `send_music`, and
`send_gif`. `upload_file(path, file_type)` uploads and returns a Rubika
file ID without sending it; `download_file(file_id)` returns downloaded bytes.

Compatibility aliases include `get_chat_info`, `edit_message`, and
`disconnect`. `register_all_endpoints(base_url)` registers the five supported
webhook endpoint types at the following paths: `update`, `inline`,
`query`, `selection`, and `search-selection`.

## Filters, middleware and plugins

```python
from ertebat import Rubika, Text, FromUser, Command

bot = Rubika("YOUR_BOT_TOKEN")

@bot.message(Text() & FromUser("USER_ID"))
async def private_text(bot, event):
    await event.reply("Text received")

@bot.message(Command("help") | Text("help"))
async def help_handler(bot, event):
    await event.reply("Help")

async def logging_middleware(bot, event, next_handler):
    print(event.type, event.chat_id)
    await next_handler()

bot.middleware(logging_middleware)
# A plugin module must expose setup(bot):
# bot.load_plugin("my_project.plugins.echo")
bot.run()
```

Filters can be combined with `&`, `|`, and `~`. Middleware uses
`middleware(bot, event, next_handler)`. Plugins are modules or callables
exposing `setup(bot)`.

## Scope and API limitations

Quiz mode is not implemented because the currently referenced Bot API method
list documents polls, not a quiz endpoint. Ertebat does not start an HTTP server:
deploy a public HTTPS route using your web framework and pass its parsed body
to `process_webhook()`. User-account/Userbot methods are intentionally outside
the token-based Bot API client.
