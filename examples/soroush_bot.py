from irubix import soroush

bot = soroush("SOROUSH_BOT_TOKEN")


@bot.command("start")
async def start(bot, event):
    await event.reply("سلام! ربات سروش‌پلاس فعاله.")


bot.run()
