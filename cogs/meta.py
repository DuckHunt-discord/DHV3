import datetime
import os
import re
from collections import Counter

import discord
from discord.ext import commands

from .utils import checks


class TimeParser:
    def __init__(self, argument):
        compiled = re.compile(r"(?:(?P<hours>\d+)h)?(?:(?P<minutes>\d+)m)?(?:(?P<seconds>\d+)s)?")
        self.original = argument
        try:
            self.seconds = int(argument)
        except ValueError as e:
            match = compiled.match(argument)
            if match is None or not match.group(0):
                raise commands.BadArgument('Failed to parse time.') from e

            self.seconds = 0
            hours = match.group('hours')
            if hours is not None:
                self.seconds += int(hours) * 3600
            minutes = match.group('minutes')
            if minutes is not None:
                self.seconds += int(minutes) * 60
            seconds = match.group('seconds')
            if seconds is not None:
                self.seconds += int(seconds)

        if self.seconds < 0:
            raise commands.BadArgument('I don\'t do negative time.')

        if self.seconds > 604800:  # 7 days
            raise commands.BadArgument('That\'s a bit too far in the future for me.')


class Meta:
    """Commands for utilities related to Discord or the Bot itself."""

    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='quit', hidden=True)
    @checks.is_owner()
    async def _quit(self):
        """Quits the bot."""
        await self.bot.logout()

    def get_bot_uptime(self):
        now = datetime.datetime.utcnow()
        delta = now - self.bot.uptime
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        if days:
            fmt = '{d} days, {h} hours, {m} minutes, and {s} seconds'
        else:
            fmt = '{h} hours, {m} minutes, and {s} seconds'

        return fmt.format(d=days, h=hours, m=minutes, s=seconds)

    @commands.command()
    async def join(self):
        """Joins a server."""
        msg = 'It is no longer possible to ask me to join via invite. So use this URL instead.\n\n'
        perms = discord.Permissions.none()
        perms.read_messages = True
        perms.send_messages = True
        perms.manage_roles = True
        perms.ban_members = True
        perms.kick_members = True
        perms.manage_messages = True
        perms.embed_links = True
        perms.read_message_history = True
        perms.attach_files = True
        await self.bot.say(msg + discord.utils.oauth_url(self.bot.client_id, perms))

    @commands.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def leave(self, ctx):
        """Leaves the server.

        To use this command you must have Manage Server permissions or have
        the Bot Admin role.
        """
        server = ctx.message.server
        try:
            await self.bot.leave_server(server)
        except:
            await self.bot.say('Could not leave..')

    @commands.command()
    async def uptime(self):
        """Tells you how long the bot has been up for."""
        await self.bot.say('Uptime: **{}**'.format(self.get_bot_uptime()))

    @commands.command()
    async def about(self):
        """Tells you information about the bot itself."""
        revision = os.popen(r'git show -s HEAD --format="%s (%cr)"').read().strip()
        result = ['**About Me:**']
        result.append('- Author: Danny#0007 (Discord ID: 80088516616269824)')
        result.append('- Library: discord.py (Python)')
        result.append('- Latest Change: {}'.format(revision))
        result.append('- Uptime: {}'.format(self.get_bot_uptime()))
        result.append('- Servers: {}'.format(len(self.bot.servers)))
        result.append('- Commands Run: {}'.format(sum(self.bot.commands_used.values())))

        # statistics
        total_members = sum(len(s.members) for s in self.bot.servers)
        total_online = sum(1 for m in self.bot.get_all_members() if m.status != discord.Status.offline)
        unique_members = set(self.bot.get_all_members())
        unique_online = sum(1 for m in unique_members if m.status != discord.Status.offline)
        channel_types = Counter(c.type for c in self.bot.get_all_channels())
        voice = channel_types[discord.ChannelType.voice]
        text = channel_types[discord.ChannelType.text]
        result.append('- Total Members: {} ({} online)'.format(total_members, total_online))
        result.append('- Unique Members: {} ({} online)'.format(len(unique_members), unique_online))
        result.append('- {} text channels, {} voice channels'.format(text, voice))
        result.append('')
        result.append('"Official" R. Danny server: https://discord.gg/0118rJdtd1rVJJfuI')
        await self.bot.say('\n'.join(result))

    @commands.command(rest_is_raw=True, hidden=True)
    @checks.is_owner()
    async def echo(self, *, content):
        await self.bot.say(content)

    @commands.command(hidden=True)
    @checks.is_owner()
    async def commandstats(self):
        msg = 'Since startup, {} commands have been used.\n{}'
        counter = self.bot.commands_used
        await self.bot.say(msg.format(sum(counter.values()), counter))

    @commands.command(pass_context=True)
    async def stats(self, ctx):
        raise NotImplementedError

    @commands.command(pass_context=True)
    async def ping(self, ctx):
        raise NotImplementedError

    @commands.command(pass_context=True)
    async def wiki(self):
        raise NotImplementedError

def setup(bot):
    bot.add_cog(Meta(bot))
