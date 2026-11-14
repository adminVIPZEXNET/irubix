from irubix import IRubix

bot = IRubix("YOUR_BOT_TOKEN")

@bot.command("start")
async def start(bot, event):
    await event.reply("سلام! ربات مستقل IRubix آماده است.")

@bot.message()
async def echo(bot, event):
    if event.text:
        await event.reply(f"شما گفتید: {event.text}")

bot.run()
