# IRubix

کتابخانه پایتون برای ساخت کلاینت روبیکا، بله، سروش‌پلاس و حساب کاربری شاد.

- کلاینت ربات برای Rubika، Bale و Soroush Plus
- کلاینت مستقل حساب کاربری Shad
- پشتیبانی از async/await و handlerهای رویداد
- مستندات فارسی

سازنده: [mahdishami](https://github.com/mahdishami)

## مستندات
- [وب‌سایت](https://adminvipzexnet.github.io/irubix/)
- [راهنمای شاد](https://adminvipzexnet.github.io/irubix/shad-guide/)
- [متدهای شاد](https://adminvipzexnet.github.io/irubix/shad-methods/)

## نصب
```bash
pip install --upgrade irubix
```

## حساب کاربری شاد
ماژول شاد یک کلاینت حساب کاربری است، نه ربات. در این نسخه باید نشست API v6 موجود را به‌صورت فایل JSON شامل کلیدهای `auth` و `private_key` (و ترجیحاً `guid`) در اختیار کلاینت قرار دهید.

```python
from irubix import shad

app = shad.Shad(session="my_shad_session.json", platform="shad_web")

@app.on_new_message()
async def on_message(event):
    print(event.text)
    await event.reply("سلام ❤️")

app.run()
```

ارسال پیام:
```python
await app.send_message("CHAT_GUID", "سلام")
```

پلتفرم‌ها: `shad_web`، `shad_pwa` و `shad_android`.

**محدودیت فعلی:** ورود اولیه با شماره تلفن و کد تأیید و متدهای پیشرفته رسانه‌ای/مدیریتی هنوز پیاده‌سازی نشده‌اند. فایل نشست و کلید خصوصی را محرمانه نگه دارید.

## مجوز
IRubix تحت مجوز MIT منتشر می‌شود.
