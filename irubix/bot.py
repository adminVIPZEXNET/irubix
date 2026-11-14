"""رابط ساده برای ساخت ربات روبیکا با استفاده از maxrubika."""

from typing import Any, Callable, Optional

from maxrubika import Bot as _MaxBot


class IRubix:
    """یک wrapper ساده روی maxrubika.Bot با متدهای کوتاه و خوانا."""

    def __init__(self, token: str, **kwargs: Any) -> None:
        if not token:
            raise ValueError("توکن ربات نباید خالی باشد.")
        self._bot = _MaxBot(token, **kwargs)

    # ---------- ارسال پیام ----------
    def send_text(self, chat_id: str, text: str, **kwargs: Any):
        """ارسال متن ساده به یک چت."""
        return self._bot.send_message(chat_id=chat_id, text=text, **kwargs)

    def send_file(
        self,
        chat_id: str,
        path: str,
        text: Optional[str] = None,
        file_type: str = "File",
        **kwargs: Any,
    ):
        """ارسال فایل از مسیر محلی."""
        if text is not None:
            kwargs["text"] = text
        return self._bot.send_file(
            chat_id=chat_id, file=path, file_type=file_type, **kwargs
        )

    def send_poll(self, chat_id: str, question: str, options: list, **kwargs: Any):
        """ارسال نظرسنجی."""
        return self._bot.send_poll(
            chat_id=chat_id, question=question, options=options, **kwargs
        )

    def send_quiz(
        self,
        chat_id: str,
        question: str,
        options: list,
        correct_option: int,
        **kwargs: Any,
    ):
        """ارسال آزمون چندگزینه‌ای با پاسخ صحیح."""
        return self._bot.send_quiz(
            chat_id=chat_id,
            question=question,
            options=options,
            correct_option=correct_option,
            **kwargs,
        )

    # ---------- دستورات و رویدادها ----------
    def command(self, names: Any) -> Callable:
        """دکوراتور برای ثبت دستور، مثلا @bot.command("start")."""
        return self._bot.on_command(names)

    def callback(self) -> Callable:
        """دکوراتور برای دکمه‌های inline."""
        return self._bot.on_callback()

    def message(self, flt: Any = None) -> Callable:
        """دکوراتور برای پیام‌ها؛ می‌توانید یک فیلتر maxrubika بدهید."""
        if flt is None:
            return self._bot.on_message()
        return self._bot.on_message(flt)

    def run(self) -> None:
        """اجرای ربات."""
        self._bot.run()

    def __getattr__(self, name: str) -> Any:
        # هر متد دیگری از maxrubika.Bot در دسترس است.
        return getattr(self._bot, name)


# نام کوتاه‌تر برای استفاده راحت‌تر
Bot = IRubix
