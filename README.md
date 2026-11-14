# IRubix

کتابخانه پایتون برای ساخت ربات در روبیکا و بله

- دو کلاینت مستقل برای Rubika و Bale
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
    await event.reply("سلام! خوش اومدی ❤️")

bot.run()
```

کلاینت بله از API مستقل https://tapi.bale.ai استفاده می‌کند. نسخه فعلی شامل long polling، فرمان‌ها، handler پیام و callback، ارسال/ویرایش/حذف پیام و ارسال عکس/سند با شناسه یا URL است. جزئیات در [راهنمای بله](https://adminvipzexnet.github.io/irubix/bale-guide/) آمده است.

## امنیت
توکن ربات را در سورس عمومی یا مخزن Git قرار ندهید. برای پروژه واقعی از متغیرهای محیطی استفاده کنید.

## مجوز
MIT
