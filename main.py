import discord
import aiohttp
from discord.ext import commands
import multidict
import aiohttp.payload as payload
from urllib.parse import urlencode, quote
import asyncio

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


class CustomFormData(aiohttp.FormData):
    def _gen_form_urlencoded(self) -> payload.BytesPayload:
        # form data (x-www-form-urlencoded)
        data = []
        for type_options, _, value in self._fields:
            data.append((type_options['name'], value))

        charset = self._charset if self._charset is not None else 'utf-8'

        if charset == 'utf-8':
            content_type = 'application/x-www-form-urlencoded'
        else:
            content_type = ('application/x-www-form-urlencoded; '
                            'charset=%s' % charset)

        return payload.BytesPayload(
            urlencode(data, doseq=False, encoding=charset,
                      quote_via=quote).encode(),
            content_type=content_type)


@bot.command(aliases=["l", "L"])
async def latex(ctx: commands.Context, *, formula: str):
    async with aiohttp.ClientSession() as session:
        async with ctx.typing():
            embed = discord.Embed()
            embed.set_author(name=ctx.message.author.display_name,
                             icon_url=str(ctx.message.author.avatar_url))
            form_data = CustomFormData()
            form_data.add_field("formula", formula)
            form_data.add_fields(multidict.MultiDict(default_data))
            async with session.post("https://www.quicklatex.com/latex3.f", data=form_data) as response:
                formula_data = (await response.text()).splitlines()
                if int(formula_data[0]) != 0:
                    await ctx.send("That isn't a valid latex expression")
                    await ctx.send(f"`{formula_data[2]}`")
                    return
                image_url = formula_data[1].split()[0]
                print("Sending", formula)
                embed.set_image(url=image_url)
                message: discord.Message = await ctx.send(embed=embed)
        try:
            before, after = await bot.wait_for("message_edit", check=lambda old, _: old.id == ctx.message.id, timeout=600)
            await message.delete()
            await bot.process_commands(after)
        except asyncio.TimeoutError:
            pass


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="quicklatex.com"))

bot.run(token)
