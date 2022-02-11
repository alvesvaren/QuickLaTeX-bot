import nextcord
from typing import Any
from nextcord.ext import commands
import asyncio
from latex_render import latex_session, render as render_latex
from io import BytesIO

bot = commands.Bot(command_prefix='$')

with open("token.txt") as file:
    token = file.read().strip()

render = lambda *args: render_latex(*args)

@bot.command(aliases=["l", "L"])
async def latex(ctx: commands.Context, *, formula: str):
    async with ctx.typing():
        embed = nextcord.Embed()
        avatar = ctx.message.author.avatar
        embed.set_author(name=ctx.message.author.display_name,
                            icon_url=str(avatar.url if avatar else None))
        with BytesIO() as image_binary:
            image = render(formula, 20, "#cecece", 4)
            image.save(image_binary, 'PNG')
            image_binary.seek(0)
            embed.set_image(url="attachment://image.png")
            file = nextcord.File(fp=image_binary, filename='image.png')
            print("Sending", formula)
            message: nextcord.Message = await ctx.send(embed=embed, file=file)
    try:
        before, after = await bot.wait_for("message_edit", check=lambda old, _: old.id == ctx.message.id, timeout=1800)
        await message.delete()
        await bot.process_commands(after)
    except asyncio.TimeoutError:
        pass


@bot.event
async def on_ready():
    await bot.change_presence(activity=nextcord.Game(name="quicklatex.com"))

with latex_session() as _render:
    render = _render
    bot.run(token)

