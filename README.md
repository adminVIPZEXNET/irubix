# IRubix

کتابخانه پایتون برای ساخت ربات در تلگرام، روبیکا، بله و سروش‌پلاس.

- کلاینت ربات برای Telegram، Rubika، Bale و Soroush Plus
- پشتیبانی از async/await و handlerهای رویداد
- بدون وابستگی runtime اضافی
- مستندات فارسی

سازنده: [mahdishami](https://github.com/mahdishami)

## مستندات
- [وب‌سایت](https://adminvipzexnet.github.io/irubix/)
- [راهنمای تلگرام](https://adminvipzexnet.github.io/irubix/telegram-guide/)
- [متدهای تلگرام](https://adminvipzexnet.github.io/irubix/telegram-methods/)
- [راهنمای روبیکا](https://adminvipzexnet.github.io/irubix/bot-guide/)
- [متدهای روبیکا](https://adminvipzexnet.github.io/irubix/bot-methods/)
- [راهنمای بله](https://adminvipzexnet.github.io/irubix/bale-guide/)
- [متدهای بله](https://adminvipzexnet.github.io/irubix/bale-methods/)
- [راهنمای سروش‌پلاس](https://adminvipzexnet.github.io/irubix/soroush-guide/)
- [متدهای سروش‌پلاس](https://adminvipzexnet.github.io/irubix/soroush-methods/)

## نصب
```bash
pip install --upgrade irubix
```

## نمونه ربات تلگرام
```python
from irubix import telegram
bot = telegram.IRubix("TELEGRAM_BOT_TOKEN")

@bot.command("start")
async def start(bot, event):
    await event.reply("سلام! خوش اومدی ❤️")

bot.run()
```

## مجوز
IRubix تحت مجوز MIT منتشر می‌شود.
