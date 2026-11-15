from irubix import bale

bot = bale.IRubix("BALE_BOT_TOKEN")


@bot.command("start")
async def start(bot, event):
    await event.reply("سلام! ربات بله فعاله.")


bot.run()
