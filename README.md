# IRubix

کتابخانه پایتون برای ساخت کلاینت روبیکا، بله، سروش‌پلاس و حساب کاربری شاد.

- کلاینت ربات برای Rubika، Bale و Soroush Plus
- کلاینت حساب کاربری Shad بر پایه MAXRubika
- پشتیبانی از async/await و handlerهای رویداد
- مستندات فارسی

سازنده IRubix: [mahdishami](https://github.com/mahdishami)

## مستندات
- [وب‌سایت مستندات](https://adminvipzexnet.github.io/irubix/)
- [راهنمای روبیکا](https://adminvipzexnet.github.io/irubix/bot-guide/)
- [راهنمای بله](https://adminvipzexnet.github.io/irubix/bale-guide/)
- [راهنمای سروش‌پلاس](https://adminvipzexnet.github.io/irubix/soroush-guide/)
- [راهنمای حساب کاربری شاد](https://adminvipzexnet.github.io/irubix/shad-guide/)
- [متدهای حساب کاربری شاد](https://adminvipzexnet.github.io/irubix/shad-methods/)

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

## حساب کاربری شاد (User Client)
شاد در IRubix از حساب کاربری و نشست استفاده می‌کند؛ توکن ربات شاد در این ماژول کاربرد ندارد. پیاده‌سازی حساب کاربری بر پایه کتابخانه [MAXRubika](https://github.com/MEH2RAB/maxrubika) و مجوز MIT آن است.

```python
from irubix import shad

app = shad.Shad(
    session="my_shad_session",
    platform="shad_web"
)

@app.on_new_message()
async def on_message(event):
    print(event.text)
    await event.reply("سلام ❤️")

app.run()
```

پلتفرم‌های پشتیبانی‌شده:
- `shad_web`
- `shad_pwa`
- `shad_android`

برای ورود اولیه، می‌توان از شماره تلفن و کد تأیید در فرایند `start()` استفاده کرد. نشست حساب را محرمانه نگه دارید و آن را در مخزن عمومی قرار ندهید.

## مجوز
IRubix تحت MIT منتشر می‌شود. ماژول Shad از MAXRubika استفاده می‌کند؛ اطلاعیه مجوز MIT و حق نشر آن پروژه در مخزن بالادستی موجود است.
