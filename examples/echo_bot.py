from irubix import Rubika

bot = Rubika("YOUR_BOT_TOKEN")


@bot.command("start")
async def start(bot, event):
    await event.reply("سلام! ربات IRubix فعاله 👋")


@bot.message()
async def echo(bot, event):
    if event.text:
        await event.reply(event.text)


bot.run()
