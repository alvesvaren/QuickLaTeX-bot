import discord
import aiohttp
from discord.ext import commands

bot = commands.Bot(command_prefix='$')

with open("token.txt") as file:
    token = file.read().strip()

default_data = {
    "fsize": "25px",
    "fcolor": "cccccc", 
    "mode": 0, 
    "out": 1,
    "errors": 1,
    "preamble": r"\usepackage{amsmath}\usepackage{amsfonts}\usepackage{amssymb}"
}
@bot.command(aliases=["l"])
async def latex(ctx: commands.Context, *, formula):
    async with aiohttp.ClientSession() as session:
        async with ctx.typing():
            embed = discord.Embed()
            embed.set_author(name=ctx.message.author.nick, icon_url=str(ctx.message.author.avatar_url))
            async with session.post("https://www.quicklatex.com/latex3.f", data={"formula": formula.replace(" ", ""), **default_data}) as response:
                formula_data = (await response.text()).splitlines()
                if int(formula_data[0]) != 0:
                    await ctx.send("That isn't a valid latex expression")
                    return
                image_url = formula_data[1].split()[0]
                print("Sending", formula)
                embed.set_image(url=image_url)
                await ctx.send(embed=embed)

bot.run(token)
