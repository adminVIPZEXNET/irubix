from irubix import soroush

bot = soroush.IRubix("SOROUSH_BOT_TOKEN")


@bot.command("start")
async def start(bot, event):
    await event.reply("سلام! ربات سروش‌پلاس فعاله.")


bot.run()
