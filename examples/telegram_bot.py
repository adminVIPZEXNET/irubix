from ertebat import telegram

bot = telegram("TELEGRAM_BOT_TOKEN")


@bot.command("start")
async def start(bot, event):
    await event.reply("سلام! ربات تلگرام فعاله.")


bot.run()
