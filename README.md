# irubix

کتابخانه‌ای ساده برای ساخت ربات روبیکا با متدهای کوتاه و خوانا. این پکیج روی [maxrubika](https://github.com/MEH2RAB/maxrubika) ساخته شده و به‌عنوان وابستگی از آن استفاده می‌کند.

## نصب

```bash
pip install git+https://github.com/adminVIPZEXNET/irubix.git
```

## نمونه سریع

```python
from irubix import IRubix

bot = IRubix("TOKEN")

@bot.command("start")
async def start(bot, event):
    await event.reply("سلام!")

bot.run()
```

## متدهای اصلی

- `send_text(chat_id, text)` ارسال متن
- `send_file(chat_id, path, text=None, file_type="File")` ارسال فایل
- `send_poll(chat_id, question, options)` ارسال نظرسنجی
- `send_quiz(chat_id, question, options, correct_option)` ارسال آزمون
- `command(names)` دکوراتور دستور
- `callback()` دکوراتور دکمه‌های inline
- `message(flt=None)` دکوراتور پیام
- `run()` اجرای ربات

هر متد دیگری از maxrubika هم به‌صورت خودکار در دسترس است.

## لایسنس

MIT. این پروژه از maxrubika (MIT) استفاده می‌کند؛ جزئیات در فایل LICENSE آمده است.
