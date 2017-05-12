# -*- coding: utf-8 -*-
# !/usr/bin/env python3.5

"""

"""
import datetime

import discord


class Logs:
    def __init__(self, bot):
        self.bot = bot
        self.channel = "297750761365045249"

    async def on_member_join(self, member):
        channel = self.bot.get_channel(self.channel)
        embed = discord.Embed()
        embed.colour = discord.Colour.green()
        embed.title = "User {u} joined".format(u=member.name + "#" + member.discriminator)
        embed.timestamp = datetime.datetime.now()
        embed.set_author(name=member.id, icon_url=member.avatar_url)
        await self.bot.send_message(channel, embed=embed)

    async def on_member_remove(self, member):
        channel = self.bot.get_channel(self.channel)
        embed = discord.Embed()
        embed.colour = discord.Colour.red()
        embed.title = "User {u} left".format(u=member.name + "#" + member.discriminator)
        embed.timestamp = datetime.datetime.now()
        embed.set_author(name=member.id, icon_url=member.avatar_url)
        await self.bot.send_message(channel, embed=embed)


def setup(bot):
    bot.add_cog(Logs(bot))
