# IRubix

کتابخانه‌ای سبک برای ساخت ربات در **روبیکا، بله، سروش‌پلاس و تلگرام** با Python و `async/await`.

## نصب

```bash
python -m pip install --upgrade irubix
```

برای نصب آخرین نسخه مخزن (بدون نیاز به Git):

```bash
python -m pip install --upgrade https://github.com/adminVIPZEXNET/irubix/archive/refs/heads/main.zip
```

## شروع سریع

در همه پیام‌رسان‌ها کلاینت مستقیماً ساخته می‌شود؛ نیازی به `.IRubix` نیست. واردکردن توکن اختیاری است: اگر توکن را ننویسید، IRubix آن را به‌صورت مخفی در ترمینال درخواست می‌کند.

فقط ماژول پیام‌رسان موردنظر را انتخاب کنید.

**روبیکا**
```python
from irubix import Rubika

bot = Rubika()  # توکن در ترمینال پرسیده می‌شود

@bot.command("start")
async def start(bot, event):
    await event.reply("سلام! ربات فعاله.")

bot.run()
```

**بله**
```python
from irubix import bale

bot = bale()  # توکن در ترمینال پرسیده می‌شود

@bot.command("start")
async def start(bot, event):
    await event.reply("سلام! ربات فعاله.")

bot.run()
```

**سروش‌پلاس**
```python
from irubix import soroush

bot = soroush()  # توکن در ترمینال پرسیده می‌شود

@bot.command("start")
async def start(bot, event):
    await event.reply("سلام! ربات فعاله.")

bot.run()
```

**تلگرام**
```python
from irubix import telegram

bot = telegram()  # توکن در ترمینال پرسیده می‌شود

@bot.command("start")
async def start(bot, event):
    await event.reply("سلام! ربات فعاله.")

bot.run()
```

## اجرای چند ربات هم‌زمان

با `MultiBot` می‌توانید چند ربات از پیام‌رسان‌های مختلف را در یک برنامه اجرا کنید:

```python
from irubix import MultiBot

app = MultiBot()
rubika = app.add("rubika", "RUBIKA_TOKEN")
telegram = app.add("telegram", "TELEGRAM_TOKEN")
bale = app.add("bale", "BALE_TOKEN")

@rubika.command("start")
async def rubika_start(bot, event):
    await event.reply("Hello from Rubika!")

@telegram.command("start")
async def telegram_start(bot, event):
    await event.reply("Hello from Telegram!")

app.run()  # همه ربات‌ها به‌صورت هم‌زمان اجرا می‌شوند
```

برای افزودن چند ربات از یک پیام‌رسان، نام یکتا تعیین کنید:

```python
first = app.add("bale", "TOKEN_1", name="bale_main")
second = app.add("bale", "TOKEN_2", name="bale_backup")
```

`app.stop()` همه ربات‌ها را متوقف می‌کند و `app.get("rubika")` یک ربات ثبت‌شده را برمی‌گرداند.

## مستندات

- [راهنمای کامل همه کلاس‌ها و نمونه‌کدها](https://adminvipzexnet.github.io/irubix/classes/)
- [مستندات کامل API روبیکا v3، متدها و مدل‌ها](docs/rubika-api-v3.md)
- [دسترسی به متدهای API بله، سروش‌پلاس و تلگرام](docs/platform-api-methods.md)

| پیام‌رسان | راهنما | متدها |
|---|---|---|
| روبیکا | [شروع سریع](https://adminvipzexnet.github.io/irubix/bot-guide/) | [فهرست متدها](https://adminvipzexnet.github.io/irubix/bot-methods/) |
| بله | [شروع سریع](https://adminvipzexnet.github.io/irubix/bale-guide/) | [فهرست متدها](https://adminvipzexnet.github.io/irubix/bale-methods/) |
| سروش‌پلاس | [شروع سریع](https://adminvipzexnet.github.io/irubix/soroush-guide/) | [فهرست متدها](https://adminvipzexnet.github.io/irubix/soroush-methods/) |
| تلگرام | [شروع سریع](https://adminvipzexnet.github.io/irubix/telegram-guide/) | [فهرست متدها](https://adminvipzexnet.github.io/irubix/telegram-methods/) |

- [وب‌سایت مستندات](https://adminvipzexnet.github.io/irubix/)
- [نمونه خروجی‌ها](https://adminvipzexnet.github.io/irubix/outputs/)
- [سؤالات متداول](https://adminvipzexnet.github.io/irubix/faq/)

## ساختار پروژه

```text
irubix/
├── __init__.py       # ورودی اصلی کتابخانه
├── bot.py            # پیاده‌سازی کلاینت روبیکا
├── _update.py        # بررسی نسخه جدید
├── multibot.py       # اجرای چند ربات
├── bale/             # کلاینت بله
├── soroush/          # کلاینت سروش‌پلاس
└── telegram/         # کلاینت تلگرام

docs/                 # مستندات
examples/             # نمونه‌کدها
tests/                # تست‌ها
```

## نکات

- سازنده مستقیم هر پیام‌رسان: `Rubika("TOKEN")`، `bale("TOKEN")`، `soroush("TOKEN")` و `telegram("TOKEN")`.
- برای سازگاری با کدهای قبلی، ویژگی‌های `.IRubix` و `.Bot` همچنان به‌عنوان alias در دسترس‌اند.

- تمام درخواست‌های API به‌صورت async اجرا می‌شوند.
- هسته کتابخانه به کتابخانه جانبی نیاز ندارد.
- هر پیام‌رسان فقط API و قابلیت‌های رسمی خودش را ارائه می‌کند.
- برای غیرفعال‌کردن بررسی نسخه جدید، متغیر محیطی `IRUBIX_DISABLE_UPDATE_CHECK=1` را تنظیم کنید.

## اجرای تست‌ها

```bash
python -m unittest discover -s tests -v
```

## مجوز

MIT

