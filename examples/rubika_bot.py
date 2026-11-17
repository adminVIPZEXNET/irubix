from ertebat import Rubika

bot = Rubika("RUBIKA_BOT_TOKEN")


@bot.command("start")
async def start(bot, event):
    await event.reply("سلام! ربات روبیکا فعاله.")


bot.run()
