# IRubix

کتابخانه پایتون برای ساخت ربات روبیکا؛ مستقل و بدون وابستگی به پکیج‌های جانبی. ارتباط HTTP، JSON، آپلود فایل و دریافت رویدادها با کتابخانه استاندارد پایتون انجام می‌شود.

## نصب

```bash
pip install git+https://github.com/adminVIPZEXNET/irubix.git
```

در Pydroid، اگر Git نصب نیست:

```bash
pip install https://github.com/adminVIPZEXNET/irubix/archive/refs/heads/main.zip
```

## نمونه ربات

```python
from irubix import IRubix

bot = IRubix("YOUR_BOT_TOKEN")

@bot.command("start")
async def start(bot, event):
    await event.reply("سلام! ربات من با IRubix مستقل اجرا می‌شود.")

@bot.message()
async def echo(bot, event):
    if event.text:
        await event.reply("شما گفتید: " + event.text)

bot.run()
```

## ارسال پیام

```python
import asyncio
from irubix import IRubix

bot = IRubix("YOUR_BOT_TOKEN")

async def main():
    await bot.send_text("CHAT_ID", "سلام از IRubix")
    await bot.send_message("CHAT_ID", "پیام دوم")

asyncio.run(main())
```

## ارسال فایل، نظرسنجی و آزمون

```python
await bot.send_file("CHAT_ID", "photo.jpg", text="تصویر", file_type="Image")
await bot.send_poll("CHAT_ID", "رنگ مورد علاقه؟", ["آبی", "قرمز"])
await bot.send_quiz("CHAT_ID", "۲ + ۲؟", ["۳", "۴"], correct_option=1)
```

متدهای شبکه‌ای async هستند؛ در هندلرها از `await` استفاده کنید. این نسخه از Bot API روبیکا در آدرس `https://botapi.rubika.ir/v3` استفاده می‌کند.

## وابستگی‌ها

هیچ وابستگی زمان اجرایی خارجی ندارد. فقط کتابخانه‌های استاندارد پایتون استفاده می‌شوند.
