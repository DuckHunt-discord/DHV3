# -*- coding: utf-8 -*-
# !/usr/bin/env python3.5

"""

"""
import json
import urllib
from urllib.parse import urlparse

import discord
import requests
from cogs import checks
from discord.ext import commands


async def json_to_embed(parsed_json: dict, ignore_keys: list = list()):
    embed = discord.Embed()
    for key in [x for x in parsed_json.keys() if x not in ignore_keys]:
        if isinstance(parsed_json[key], str) or isinstance(parsed_json[key], int) or isinstance(parsed_json[key], float):
            embed.add_field(name=key, value=parsed_json[key])

    return embed


async def dl_json(url: str):
    r = requests.get(url)
    return json.loads(r.content)


class Httpcat():
    def __init__(self, bot):
        self.bot = bot

    @checks.have_required_level(1)
    @commands.command(pass_context=True)
    async def cat(self, ctx, err: str):
        """returns HTTP error from http.cat"""
        embed = discord.Embed()
        embed.colour = discord.Colour.dark_red()
        embed.title = "Error " + err
        embed.url = "https://http.cat/" + err
        embed.set_image(url="https://http.cat/" + err)
        await self.bot.say(embed=embed)
        await self.bot.delete_message(ctx.message)

    @checks.have_required_level(1)
    @commands.command(pass_context=True, aliases=["avatar"])
    async def avatars(self, ctx, avatar: str):
        """Returns an (adorable) avatar for a specified string"""
        embed = discord.Embed()
        embed.colour = discord.Colour.dark_gold()
        embed.title = "Avatar of " + avatar
        embed.url = "https://api.adorable.io/avatars/285/" + avatar
        embed.set_image(url="https://api.adorable.io/avatars/285/" + avatar)
        await self.bot.say(embed=embed)
        await self.bot.delete_message(ctx.message)

    @checks.have_required_level(1)
    @commands.command(pass_context=True, aliases=["chucknorris", "cn"])
    async def chuck(self, ctx):
        """Returns an (adorable) avatar for a specified string"""
        data = await dl_json("https://api.chucknorris.io/jokes/random")
        embed = discord.Embed()
        embed.colour = discord.Colour.dark_blue()
        embed.title = "Chuck Norris once said "
        embed.description = data["value"]
        embed.url = data["url"]
        # embed.set_image(url=data["icon_url"])
        await self.bot.say(embed=embed)
        await self.bot.delete_message(ctx.message)

    @checks.have_required_level(1)
    @commands.command(pass_context=True, aliases=["donald", "dt", "donaldtrump"])
    async def trump(self, ctx):
        """Returns a random quote from Tronald Dump"""
        data = await dl_json("https://api.tronalddump.io/random/quote")
        embed = await json_to_embed(data, ["quote_id", "tags", "updated_at", "created_at", "_links", "_embedded", "value"])
        embed.colour = discord.Colour.dark_teal()
        embed.title = "Donald Trump said..."
        embed.url = data["_embedded"]["source"][0]["url"]
        embed.description = data["value"]
        await self.bot.say(embed=embed)
        await self.bot.delete_message(ctx.message)

    @checks.have_required_level(1)
    @commands.command(pass_context=True)
    async def logo(self, ctx, company_website: str):
        """Get a company logo from their website."""
        # uri = urlparse(company_website)
        # domain = str(uri.netloc)
        domain = company_website
        embed = discord.Embed()
        embed.colour = discord.Colour.dark_gold()
        embed.title = domain
        embed.description = "Here is the logo you asked for!"
        # embed.url = str(uri.geturl())
        embed.url = "https://" + company_website
        embed.set_image(url="https://logo.clearbit.com/" + domain)
        await self.bot.say(embed=embed)
        await self.bot.delete_message(ctx.message)

    @checks.have_required_level(2)
    @commands.command(pass_context=True, aliases=["lang", "detectlanguage"])
    async def language(self, ctx, *, text: str):
        """Get language used in a text using apilayer.net language API. Limited to 1 000+20% calls a month          """
        KEY = "0355ca4717378980774ef1166581f02b"
        encoded_query = urllib.parse.quote_plus(text)
        data = await dl_json("http://apilayer.net/api/detect?access_key=" + KEY + "&query=" + encoded_query)
        if data["success"]:
            embed = await json_to_embed(data["results"][0])
            embed.colour = discord.Colour.dark_green()
            embed.title = "Language detection"
            embed.description = text
            embed.set_image(url="https://flagpedia.net/data/flags/big/" + data["results"][0]["language_code"] + ".png")
            await self.bot.say(embed=embed)
            await self.bot.delete_message(ctx.message)
        else:
            await self.bot.say("Language detection failed")


def setup(bot):
    bot.add_cog(Httpcat(bot))
