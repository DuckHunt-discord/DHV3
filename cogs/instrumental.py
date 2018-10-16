import asyncio
import collections
import os

import psutil

import discord
from instrumental_agent import Agent

from cogs.helpers import ducks


class Instrumental:
    def __init__(self, bot):
        self.bot = bot
        self.i = Agent("2bedc491d850cdc141ed4f0e9a1a6c60", enabled=True)

    async def on_message(self, message):
        self.i.increment('dh.events.message')

    async def on_guild_join(self, guild):
        self.i.gauge('dh.performance.guilds', len(self.bot.guilds))
        self.i.gauge('dh.performance.large_guilds', len([g for g in self.bot.guilds if g.large]))

    async def on_guild_remove(self, guild):
        self.i.gauge('dh.performance.guilds', len(self.bot.guilds))
        self.i.gauge('dh.performance.large_guilds', len([g for g in self.bot.guilds if g.large]))

    async def on_member_join(self, member):
        self.i.gauge('dh.performance.members', len(self.bot.users))

    async def on_member_remove(self, member):
        self.i.gauge('dh.performance.members', len(self.bot.users))

    async def update_other_values(self):
        # Performance Metrics

        self.i.gauge('dh.performance.memory_used', round(psutil.Process(os.getpid()).memory_info()[0] / 2. ** 30 * 1000, 5))
        self.i.gauge('dh.performance.loop_latency', self.bot.loop_latency)
        self.i.gauge('dh.performance.discord_latency', max(0, self.bot.latency))
        self.i.gauge('dh.performance.enabled_channels', len(self.bot.ducks_planning.keys()))

        # Ducks
        duck_types_counter = collections.Counter([type(d).__name__ for d in self.bot.ducks_spawned])

        for duck_type, duck_count in duck_types_counter.most_common():
            self.i.gauge(f'dh.ducks.{duck_type}', duck_count)

    async def update_periodic(self):
        while True:
            await self.update_other_values()
            await asyncio.sleep(60)


def setup(bot):
    ins = Instrumental(bot)
    bot.add_cog(ins)
    bot.loop.create_task(ins.update_periodic())

