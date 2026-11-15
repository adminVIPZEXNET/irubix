# IRubix

کتابخانه‌ای سبک برای ساخت ربات در **روبیکا، بله، سروش‌پلاس و تلگرام** با Python و `async/await`.

## نصب

```bash
python -m pip install --upgrade irubix
```

برای نصب آخرین نسخه مخزن:

```bash
python -m pip install --upgrade git+https://github.com/adminVIPZEXNET/irubix.git
```

## شروع سریع

فقط ماژول پیام‌رسان و توکن همان ربات را انتخاب کنید.

**روبیکا**
```python
from irubix import rubika

bot = rubika.IRubix("BOT_TOKEN")

@bot.command("start")
async def start(bot, event):
    await event.reply("سلام! ربات فعاله.")

bot.run()
```

**بله**
```python
from irubix import bale

bot = bale.IRubix("BOT_TOKEN")

@bot.command("start")
async def start(bot, event):
    await event.reply("سلام! ربات فعاله.")

bot.run()
```

**سروش‌پلاس**
```python
from irubix import soroush

bot = soroush.IRubix("BOT_TOKEN")

@bot.command("start")
async def start(bot, event):
    await event.reply("سلام! ربات فعاله.")

bot.run()
```

**تلگرام**
```python
from irubix import telegram

bot = telegram.IRubix("BOT_TOKEN")

@bot.command("start")
async def start(bot, event):
    await event.reply("سلام! ربات فعاله.")

bot.run()
```

## مستندات

- [راهنمای کامل همه کلاس‌ها و نمونه‌کدها](https://adminvipzexnet.github.io/irubix/classes/)

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
├── bot.py            # کلاینت روبیکا
├── _update.py        # بررسی نسخه جدید
├── bale/             # کلاینت بله
├── soroush/          # کلاینت سروش‌پلاس
└── telegram/         # کلاینت تلگرام

docs/                 # مستندات
examples/             # نمونه‌کدها
tests/                # تست‌ها
```

## نکات

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
