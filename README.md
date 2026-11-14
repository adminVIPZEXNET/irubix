# IRubix

کتابخانه پایتون برای ساخت ربات در روبیکا، بله و سروش‌پلاس

- سه کلاینت مستقل برای Rubika، Bale و Soroush Plus
- بدون وابستگی خارجی در زمان اجرا
- پشتیبانی از async/await و decorator
- مناسب Pydroid 3 و محیط‌های معمول پایتون

سازنده: [mahdishami](https://github.com/mahdishami)

## مستندات
- [وب‌سایت مستندات](https://adminvipzexnet.github.io/irubix/)
- [راهنمای روبیکا](https://adminvipzexnet.github.io/irubix/bot-guide/)
- [متدهای روبیکا](https://adminvipzexnet.github.io/irubix/bot-methods/)
- [راهنمای بله](https://adminvipzexnet.github.io/irubix/bale-guide/)
- [متدهای بله](https://adminvipzexnet.github.io/irubix/bale-methods/)
- [راهنمای سروش‌پلاس](https://adminvipzexnet.github.io/irubix/soroush-guide/)
- [متدهای سروش‌پلاس](https://adminvipzexnet.github.io/irubix/soroush-methods/)

## نصب
```bash
pip install --upgrade https://github.com/adminVIPZEXNET/irubix/archive/refs/heads/main.zip
```

## ربات روبیکا
```python
from irubix import IRubix

bot = IRubix("RUBIKA_BOT_TOKEN")

@bot.command("start")
async def start(bot, event):
    await event.reply("سلام از روبیکا!")

bot.run()
```

## ربات بله
```python
from irubix import bale

bot = bale.IRubix("BALE_BOT_TOKEN")

@bot.command("start")
async def start(bot, event):
    await event.reply("سلام از بله!")

bot.run()
```

## ربات سروش‌پلاس
```python
from irubix import soroush

bot = soroush.IRubix("SOROUSH_BOT_TOKEN")

@bot.command("start")
async def start(bot, event):
    await event.reply("سلام از سروش‌پلاس!")

bot.run()
```

کلاینت سروش‌پلاس از API رسمی `https://api.splus.ir` استفاده می‌کند و شامل long polling، فرمان‌ها، handler پیام و callback، ارسال/ویرایش/حذف پیام، فوروارد پیام و مدیریت webhook است.

## امنیت
توکن ربات را در سورس عمومی یا مخزن Git قرار ندهید. برای پروژه واقعی از متغیرهای محیطی استفاده کنید.

## مجوز
MIT
