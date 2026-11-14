from irubix import IRubix

bot = IRubix("TOKEN")

@bot.command("start")
async def start(bot, event):
    await event.reply("سلام! ربات irubix آماده است 👋")

@bot.message()
async def echo(bot, event):
    await event.reply(f"شما گفتید: {event.text}")

bot.run()
