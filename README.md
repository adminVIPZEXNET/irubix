<p align="center">
  <img src="assets/irubix-logo.svg" alt="IRubix logo" width="300">
</p>

# IRubix

**کتابخانه سریع و مستقل پایتون برای ساخت ربات روبیکا**

- بدون وابستگی خارجی؛ فقط کتابخانه‌های استاندارد Python
- پشتیبانی از async/await
- دریافت پیام با polling و مدیریت رویدادها با decorator
- ارسال پیام، نظرسنجی، فایل و امکانات مدیریتی
- قابل استفاده در Pydroid 3 و محیط‌های معمول پایتون

**سازنده:** [mahdishami](https://github.com/mahdishami)

**کانال:** https://Rubika.ir/Liberyirubix

## نصب

در Pydroid 3 (بدون نیاز به Git):

```bash
pip install --upgrade https://github.com/adminVIPZEXNET/irubix/archive/refs/heads/main.zip
```

در محیطی که Git نصب است:

```bash
pip install --upgrade git+https://github.com/adminVIPZEXNET/irubix.git
```

## شروع سریع

```python
from irubix import IRubix

bot = IRubix("YOUR_BOT_TOKEN")

@bot.command("start")
async def start(bot, event):
    await event.reply("سلام! به ربات من خوش آمدید.")

@bot.message()
async def echo(bot, event):
    if event.text:
        await event.reply(event.text)

bot.run()
```

## ارسال پیام

```python
import asyncio
from irubix import IRubix

bot = IRubix("YOUR_BOT_TOKEN")

async def main():
    await bot.send_text("CHAT_ID", "سلام از IRubix!")

asyncio.run(main())
```

## مرجع کامل متدها

در این بخش تمام متدهای عمومی کلاس `IRubix` در نسخه فعلی کتابخانه، همراه با امضا و کاربردشان آمده است. متدهای شبکه‌ای را باید با `await` فراخوانی کنید؛ متدهای ثبت handler و کنترل اجرا معمولی هستند.

### ساخت ربات

```python
IRubix(token: str, *, timeout: float = 30, base_url: str | None = None)
```

- `token`: توکن ربات روبیکا.
- `timeout`: مهلت درخواست شبکه بر حسب ثانیه؛ پیش‌فرض ۳۰.
- `base_url`: آدرس پایه API سفارشی؛ در حالت عادی نیازی به تغییر آن نیست.

### متدهای عمومی و امضاها

| متد | امضا | توضیح |
| --- | --- | --- |
| `request` | `(self, method: str, input: dict \| None = None)` | فراخوانی مستقیم هر متد Bot API به‌صورت async. |
| `get_me` | `(self)` | دریافت اطلاعات ربات با `getMe`. |
| `get_chat` | `(self, chat_id: str)` | دریافت اطلاعات یک گفتگو. |
| `get_file` | `(self, file_id: str)` | دریافت اطلاعات و نشانی دانلود فایل. |
| `send_text` | `(self, chat_id: str, text: str, **kwargs)` | ارسال پیام متنی؛ گزینه‌های مجاز شامل `metadata`، `chat_keypad`، `inline_keypad`، `reply_to_message_id`، `disable_notification` و `chat_keypad_type` هستند. |
| `send_message` | `(self, chat_id: str, text: str, **kwargs)` | نام جایگزین `send_text` با همان گزینه‌ها. |
| `send_poll` | `(self, chat_id: str, question: str, options: list[str])` | ارسال نظرسنجی؛ فهرست گزینه‌ها باید دست‌کم دو گزینه داشته باشد. |
| `send_quiz` | `(self, *args, **kwargs)` | در نسخه فعلی اجرا نمی‌شود و `NotImplementedError` می‌دهد؛ حالت Quiz در Bot API رسمی فعلی مستند نشده است. |
| `forward_message` | `(self, from_chat_id: str, message_id: str, to_chat_id: str, disable_notification: bool = False)` | انتقال پیام از یک گفتگو به گفتگوی دیگر. |
| `edit_message_text` | `(self, chat_id: str, message_id: str, text: str)` | ویرایش متن پیام. |
| `delete_message` | `(self, chat_id: str, message_id: str)` | حذف پیام. |
| `ban_chat_member` | `(self, chat_id: str, user_id: str)` | مسدود کردن کاربر در گروه یا کانال. |
| `unban_chat_member` | `(self, chat_id: str, user_id: str)` | رفع مسدودیت کاربر. |
| `send_file` | `(self, chat_id: str, path: str \| Path \| bytes, text: str \| None = None, file_type: str = "File", **kwargs)` | بارگذاری فایل و ارسال آن؛ `path` مسیر فایل یا داده باینری است. می‌توان `file_name` و گزینه‌های پاسخ/کیبورد را نیز در `kwargs` داد. |
| `command` | `(self, names)` | decorator ثبت یک یا چند دستور مانند `start` یا `["start", "help"]`. |
| `message` | `(self, flt=None)` | decorator ثبت handler پیام؛ `flt` می‌تواند تابع فیلتر رویداد باشد. |
| `callback` | `(self)` | decorator ثبت handler کلیک دکمه‌های inline. |
| `start` | `(self, poll_interval: float = 1.0, limit: int = 100)` | شروع دریافت آپدیت‌ها با polling به‌صورت async. |
| `stop` | `(self)` | درخواست توقف حلقه polling. |
| `run` | `(self, poll_interval: float = 1.0, limit: int = 100)` | اجرای ربات؛ بیرون event loop خودش اجرا می‌کند و داخل event loop باید coroutine برگشتی را await کنید. |

### نمونه ثبت handlerها

```python
from irubix import IRubix

bot = IRubix("YOUR_BOT_TOKEN")

@bot.command("start")
async def start_handler(bot, event):
    await event.reply("سلام! ربات فعاله.")

@bot.command(["help", "about"])
async def help_handler(bot, event):
    await event.reply("راهنمای ربات")

@bot.message()
async def message_handler(bot, event):
    if event.text:
        await event.reply(event.text)

@bot.callback()
async def callback_handler(bot, event):
    print("Callback:", event.button_id)

bot.run()
```

### شیء Event

هر handler دو آرگومان می‌گیرد: `bot` و `event`. ویژگی‌های قابل استفاده در `event`:

| ویژگی یا متد | کاربرد |
| --- | --- |
| `event.bot` | نمونه ربات مربوط به رویداد. |
| `event.raw` | داده خام آپدیت. |
| `event.update` | همان داده آپدیت خام. |
| `event.type` | نوع رویداد. |
| `event.update_type` | نوع آپدیت؛ برابر با `event.type`. |
| `event.message` | اطلاعات پیام به شکل دیکشنری. |
| `event.chat_id` | شناسه گفتگو، در صورت وجود. |
| `event.message_id` | شناسه پیام، در صورت وجود. |
| `event.text` | متن پیام؛ اگر موجود نباشد رشته خالی. |
| `event.sender_id` | شناسه فرستنده، در صورت وجود. |
| `event.button_id` | شناسه یا داده دکمه callback، در صورت وجود. |
| `await event.reply(text, **kwargs)` | پاسخ به همان گفتگو؛ در صورت وجود شناسه پیام، پاسخ به آن پیام متصل می‌شود. |

### نکات مربوط به اجرا و درخواست‌ها

- `start()` و `run()` به‌طور پیش‌فرض با فاصله یک ثانیه آپدیت‌ها را بررسی می‌کنند.
- `poll_interval` نباید کمتر از `0.1` ثانیه باشد.
- `limit` باید بین ۱ تا ۱۰۰ باشد.
- اگر از قبل داخل یک تابع async یا event loop هستید، از `await bot.start()` یا `await bot.run()` استفاده کنید.
- متد `stop()` مقدار پرچم توقف را تغییر می‌دهد؛ آن را برای متوقف کردن polling فراخوانی کنید.
- خطاهای API با `RubikaAPIError` گزارش می‌شوند.
- `command`، `message` و `callback` decorator هستند و برای ثبت تابع handler استفاده می‌شوند.

## نکات

- تمام درخواست‌های شبکه‌ای async هستند؛ داخل handlerها از `await` استفاده کنید.
- بازه پیش‌فرض بررسی پیام‌ها یک ثانیه است. می‌توانید با `bot.run(poll_interval=0.5)` آن را تغییر دهید.
- برای جلوگیری از فشار غیرضروری به API، مقدار کمتر از ۰٫۱ ثانیه مجاز نیست.
- حالت Quiz در مستندات فعلی Bot API روبیکا تعریف نشده؛ بنابراین `send_quiz` عمداً خطای `NotImplementedError` می‌دهد.
- توکن ربات را در کد عمومی یا مخزن GitHub قرار ندهید.

## وابستگی‌ها

IRubix در زمان اجرا هیچ پکیج جانبی نیاز ندارد. `setuptools` فقط برای فرایند نصب بسته استفاده می‌شود.

## منابع

- مستندات رسمی: https://rubika.ir/botapi/methods
- مخزن مرجع بررسی الگوها: https://github.com/MEH2RAB/maxrubika

IRubix به‌صورت مستقل پیاده‌سازی شده و کد یا وابستگی اجرایی MAXRubika را وارد نمی‌کند.
