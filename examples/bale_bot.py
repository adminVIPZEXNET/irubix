from ertebat import bale

bot = bale("BALE_BOT_TOKEN")


@bot.command("start")
async def start(bot, event):
    await event.reply("سلام! ربات بله فعاله.")


bot.run()
