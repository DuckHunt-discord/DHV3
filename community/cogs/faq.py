# -*- coding: utf-8 -*-
# !/usr/bin/env python3.5

"""

"""
import discord
from cogs import checks
from discord.ext import commands


async def send_embed(bot, message, embed, user=None):
    edit_message = "FAQ"

    if user:
        await bot.send_message(message.channel, content=user.mention, embed=embed)
    else:
        await bot.send_message(message.channel, content=edit_message, embed=embed)


class Faq():
    def __init__(self, bot):
        self.bot = bot
        self.footer = "DuckHunt community bot by Eyesofcreeper"

    @checks.have_required_level(1, warn=False)
    @commands.group(pass_context=True)
    async def faq(self, ctx):
        """Get info on multiple topics"""
        # await self.bot.delete_message(ctx.message)
        if ctx.invoked_subcommand is None:
            await self.bot.say('Invalid faq command passed...')
            await self.bot.say("""```
- * <- You are here
- duckhunt
  |- *
  |- website
  |- howtoplay
  |- howtoconfigure
  |- noselfhost
  |- typebang

```""")

    @checks.have_required_level(1)
    @faq.group(pass_context=True)
    async def duckhunt(self, ctx):

        if str(ctx.invoked_subcommand) == "faq duckhunt":
            embed = discord.Embed()
            embed.colour = discord.Colour.dark_green()
            embed.title = "DuckHunt"
            embed.url = "https://api-d.com"
            embed.description = "DuckHunt is a game made by Eyesofcreeper. Named as the game on NES, the goal is to be the best duck hunter on a server."
            embed.add_field(name="How does it work?", value="You have to kill ducks, using the command `!bang`. But there is more than that. You’ll have to reload your weapon (use `!reload`) and buy objects to improve your efficiency or to piss off other hunters.", inline=False)
            embed.add_field(name="Sounds impressive!", value="Yeah, I have to admit that the game is really fun.", inline=False)
            embed.add_field(name="I'd like to learn more.", value="Our website will help you! Go to https://api-d.com.", inline=False)
            embed.set_image(url="https://api-d.com/duckhunt.jpg")
            embed.set_footer(text=self.footer, icon_url=self.bot.user.avatar_url)
            await send_embed(self.bot, ctx.message, embed)

    @checks.have_required_level(1)
    @duckhunt.command(name="website", pass_context=True)
    async def dh_website(self, ctx, user: discord.Member = None):
        embed = discord.Embed()
        embed.colour = discord.Colour.dark_green()
        embed.title = "DuckHunt - Website"
        embed.url = "https://api-d.com"
        embed.description = "Our website is brand new and online at https://api-d.com."
        embed.add_field(name="Install the bot", value="https://api-d.com/install-the-bot.html", inline=False)
        embed.add_field(name="Bot settings", value="https://api-d.com/bot-settings.html", inline=False)
        embed.add_field(name="Shop items", value="https://api-d.com/shop-items.html", inline=False)
        embed.add_field(name="Command list", value="https://api-d.com/command-list.html", inline=False)
        embed.add_field(name="Need more help?", value="Join the official DuckHunt discord server at https://discord.gg/2BksEkV", inline=False)
        # embed.set_image(url="https://api-d.com/duckhunt.jpg")
        embed.set_footer(text=self.footer, icon_url=self.bot.user.avatar_url)
        await send_embed(self.bot, ctx.message, embed, user)

    @checks.have_required_level(1)
    @duckhunt.command(name="howtoplay", pass_context=True)
    async def dh_howtoplay(self, ctx, user: discord.Member = None):
        embed = discord.Embed()
        embed.colour = discord.Colour.dark_green()
        embed.title = "DuckHunt - How to play"
        embed.url = "https://api-d.com"
        embed.description = "DuckHunt is a simple game to play, but there are many things you can do! Once you see a duck (-,,.-'`'°-,,.-'`'°  _º-  COUAAACK), you can start to play."
        embed.add_field(name="Most used commands", value="Of course, `!bang` and `!reload` are the most important commands. If you see a duck, you'll have to type `!bang` to kill it. But, beware, you weapon can jam, run out of bullets and many more things. If it's the case, try to `!reload` it.", inline=False)
        embed.add_field(name="Shop", value="If you have enough experience points, you can buy some items from this list: https://api-d.com/shop-items.html with your experience (using the command `!shop [item number]`). For exemple, you can buy another bullet with `!shop 1`.", inline=False)
        embed.add_field(name="Git gud", value="To be the best hunter, you need to be aware of a lot of statistics. You can see them with `!duckstats`. You should also look at the top scores on the channel with `!top`", inline=False)
        embed.add_field(name="Full command list", value="There is a lot more to discover. You can always view the full command list here: https://api-d.com/command-list.html", inline=False)
        embed.add_field(name="Need more help?", value="Join the official DuckHunt discord server at https://discord.gg/2BksEkV", inline=False)
        # embed.set_image(url="https://api-d.com/duckhunt.jpg")
        embed.set_footer(text=self.footer, icon_url=self.bot.user.avatar_url)
        await send_embed(self.bot, ctx.message, embed, user)

    @checks.have_required_level(1)
    @duckhunt.command(name="howtoconfigure", pass_context=True, aliases=["howtosetup", "config", "setup"])
    async def dh_howtoconfigure(self, ctx, user: discord.Member = None):
        embed = discord.Embed()
        embed.colour = discord.Colour.dark_green()
        embed.title = "DuckHunt - How to configure the bot"
        embed.url = "https://api-d.com"
        embed.description = "Configuring the bot is easy, but you'll have to follow the instructions carefully"
        embed.add_field(name="Invite the bot", value="If you haven't done so already, you will have to invite the bot by clicking here: https://discordapp.com/oauth2/authorize?&client_id=187636051135823872&scope=bot&permissions=68320256", inline=False)
        embed.add_field(name="Claim the server", value="You have invited the bot and given him the required permissions? Great! Now it's time to type on **any** channel the `!claimserver` command to make yourself an admin on the bot. ", inline=False)
        embed.add_field(name="Create channels", value="You will now need to be on the channel(s) where you want ducks to spawn on. Type `!add_channel` on each of them.", inline=False)
        embed.add_field(name="Warp up", value="The bot is set up with the default configuration. You can change settings with the `!settings set [parameter] [value]`. See the available settings table at http://api-d.com/bot-settings.html.", inline=False)
        embed.add_field(name="Need more help?", value="Join the official DuckHunt discord server at https://discord.gg/2BksEkV.", inline=False)
        # embed.set_image(url="https://api-d.com/duckhunt.jpg")
        embed.set_footer(text=self.footer, icon_url=self.bot.user.avatar_url)
        await send_embed(self.bot, ctx.message, embed, user)

    @checks.have_required_level(1)
    @duckhunt.command(name="noselfhost", pass_context=True, aliases=["selfhost"])
    async def dh_noselfhost(self, ctx, user: discord.Member = None):
        embed = discord.Embed()
        embed.colour = discord.Colour.dark_green()
        embed.title = "DuckHunt - Please do not self host it"
        embed.url = "https://api-d.com"
        embed.description = "In the past, a lot of users wanted to self host their own copy of duckhunt. Self hosting is possible (well, sort of), but I **strongly** discourage it."
        embed.add_field(name="1st reason", value="Server Owners want to self host to have a better uptime, or more control, but the official bot already has 99.8% uptime. A lot of control is provided with the settings command, there isn't anything else to configure.", inline=False)
        embed.add_field(name="2nd reason", value="Self hosting is bad because I can't see bugs, stats and a lot of metrics I use to guess what I should do first.", inline=False)
        embed.add_field(name="3rd reason", value="Self hosting the bot means you'll get (almost) no support and you will be left alone trying to install it. Updates to the git repo are frequent and you'll have to do them quickly on each release.", inline=False)
        embed.add_field(name="4th reason", value="If you were self hosting and want to go back to the official version, you can't. I can't merge two databases, as this implies a security risk for me and the users.", inline=False)
        embed.add_field(name="Need more help?", value="A lot of others reasons exist. You may discuss that with us on the official DuckHunt discord server at https://discord.gg/2BksEkV", inline=False)
        # embed.set_image(url="https://api-d.com/duckhunt.jpg")
        embed.set_footer(text=self.footer, icon_url=self.bot.user.avatar_url)
        await send_embed(self.bot, ctx.message, embed, user)

    @checks.have_required_level(1)
    @duckhunt.command(name="typebang", pass_context=True)
    async def dh_typebang(self, ctx, user: discord.Member = None):
        embed = discord.Embed()
        embed.colour = discord.Colour.dark_green()
        embed.title = "DuckHunt - When you see a duck"
        embed.url = "https://api-d.com"
        embed.description = "Here is a quick hint for ya... Once you see a duck, type `!bang`. Type `!reload` after to reload your weapon or to unjam it."
        embed.add_field(name="What's a duck?", value="A duck looks like this: `-,,.-'`'°-,,.-'`'°  _º-  COUAAACK`.", inline=False)
        embed.add_field(name="Full command list", value="There are a lot more commands. Check out the full command list here: https://api-d.com/command-list.html", inline=False)
        embed.add_field(name="Need more help?", value="Join the official DuckHunt discord server at https://discord.gg/2BksEkV", inline=False)
        embed.set_image(url="https://api-d.com/duckhunt.jpg")
        embed.set_footer(text=self.footer, icon_url=self.bot.user.avatar_url)
        await send_embed(self.bot, ctx.message, embed, user)


def setup(bot):
    bot.add_cog(Faq(bot))
