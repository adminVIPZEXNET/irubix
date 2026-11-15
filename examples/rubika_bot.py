from irubix import Rubika

bot = Rubika.IRubix("RUBIKA_BOT_TOKEN")


@bot.command("start")
async def start(bot, event):
    await event.reply("سلام! ربات روبیکا فعاله.")


bot.run()
