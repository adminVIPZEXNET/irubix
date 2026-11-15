# IRubix Feature Toolkit

All helpers below are optional, platform-neutral utilities. They do not add unsupported
features to a messaging API. AI and cloud integrations use callbacks supplied by you;
webhook handling validates a request after your HTTP framework receives it.

## Imports

```python
from irubix import (
    PluginManager, MiddlewareManager, RateLimiter, ConversationManager,
    BotStats, CommandPermissions, MessageBuilder, FileManager,
    AIAdapter, CloudStorageAdapter, AutoReconnect, WebhookAdapter,
    DeveloperConsole, SmartErrorHandler,
)
```

## Plugins

A plugin is a local Python file. It may expose synchronous `setup(app)` and
`teardown(app)` functions. Only load trusted code.

```python
plugins = PluginManager(app)
plugins.load("plugins/welcome.py")
print(plugins.list())
plugins.unload("welcome")
```

## Middleware

Middleware receives the context and a `next_call` callback.

```python
middleware = MiddlewareManager()

async def logger(context, next_call):
    print("before")
    await next_call()
    print("after")

middleware.add(logger)
await middleware.execute(handler, event)
```

## Conversations

```python
conversations = ConversationManager()
conversations.begin(chat_id, data={"step": "name"})
await conversations.feed(chat_id, "Ada")
answer = await conversations.wait(chat_id, timeout=60)
conversations.end(chat_id)
```

Call `feed` from your message handler. A conversation queue is in-memory and is
cleared when the process exits.

## Rate limiting, statistics and permissions

```python
limiter = RateLimiter(rate=5, per=1)  # five tokens per second
await limiter.acquire(chat_id)

stats = BotStats()
stats.record_message("rubika")
stats.record_error("network")
print(stats.snapshot())

permissions = CommandPermissions()
permissions.set_role(user_id, "admin")
if permissions.allows(user_id, "ban"):
    ...
```

## Message and file helpers

```python
message = MessageBuilder("Hello").reply_to_message(message_id)
await message.send(bot, chat_id)

storage = FileManager("./bot_files")
storage.save("notes/hello.txt", "Hello")
print(storage.read("notes/hello.txt", text=True))
```

FileManager confines paths to its configured root. It is local disk storage, not cloud
storage.

## AI and cloud adapters

Supply your own provider functions; credentials and network clients remain under your
control.

```python
ai = AIAdapter(my_async_generate_function)
answer = await ai.ask("Summarize this message")

cloud = CloudStorageAdapter(upload=my_upload, download=my_download)
remote_id = await cloud.upload("report.txt", b"report")
data = await cloud.download("report.txt")
```

## Reliability, webhook and diagnostics

```python
await AutoReconnect(bot, initial_delay=1, max_delay=30).run()

webhook = WebhookAdapter(handler=process_update, secret="YOUR_WEBHOOK_SECRET")
await webhook.handle(request_json, request_secret)

logger = DeveloperConsole.configure()
errors = SmartErrorHandler(callback=notify_admin)
await errors.handle(exception, context=event)
```

AutoReconnect retries failures from `client.start()`; use it instead of calling
`bot.run()` when you need a custom retry policy. WebhookAdapter is a request validator
and dispatcher, not an HTTP server. Mount it in an ASGI or other HTTP framework.
