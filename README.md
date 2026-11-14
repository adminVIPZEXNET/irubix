# IRubix

کتابخانه پایتون برای ساخت ربات در روبیکا، بله و سروش‌پلاس.

- کلاینت ربات برای Rubika
- پشتیبانی از ربات‌های Bale و Soroush Plus
- پشتیبانی از async/await و handlerهای رویداد
- مستندات فارسی

سازنده: [mahdishami](https://github.com/mahdishami)

## مستندات
- [وب‌سایت](https://adminvipzexnet.github.io/irubix/)
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

## نمونه استفاده
```python
from irubix import IRubix

bot = IRubix("BOT_TOKEN")

@bot.command("start")
async def start(bot, event):
    await event.reply("سلام! خوش اومدی ❤️")

bot.run()
```

## مجوز
IRubix تحت مجوز MIT منتشر می‌شود.
