# -*- coding: utf-8 -*-
import json
import aiohttp
import asyncio

DISCORD_BOTS_API = 'https://bots.discord.pw/api'
DISCORD_BOTS_ORG_API = 'https://discordbots.org/api'


class Carbonitex:
    """Cog for updating bots.discord.pw bot information."""

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    def __unload(self):
        # pray it closes
        self.bot.loop.create_task(self.session.close())

    async def update(self):

        payload = json.dumps({
            'server_count': len(self.bot.guilds)
        })

        ## DISCORD BOTS ##


        headers = {
            'authorization': self.bot.bots_discord_pw_key,
            'content-type' : 'application/json'
        }

        url = '{0}/bots/{1.user.id}/stats'.format(DISCORD_BOTS_API, self.bot)
        async with self.session.post(url, data=payload, headers=headers) as resp:
            self.bot.logger.info('Bots_discord_pw statistics returned {0.status} for {1}'.format(resp, payload))


        payload = json.dumps({
            'server_count': len(self.bot.guilds),
            'shard_count': len(self.bot.shards)
        })

        ## DISCORD BOTS ORG ##
        headers = {
            'authorization': self.bot.discordbots_org_key,
            'content-type' : 'application/json'
        }
        url = '{0}/bots/{1.user.id}/stats'.format(DISCORD_BOTS_ORG_API, self.bot)
        async with self.session.post(url, data=payload, headers=headers) as resp:
            self.bot.logger.info('Discordbots_org statistics returned {0.status} for {1}'.format(resp, payload))

    async def on_guild_join(self, server):
        self.bot.logger.info("## New server {name} + {members} members ##".format(name=server.name, members=server.member_count))
        await self.update()

    async def on_guild_remove(self, server):
        self.bot.logger.info("## Server removed {name} - {members} members ##".format(name=server.name, members=server.member_count))
        await self.update()

    async def on_ready(self):
        await asyncio.sleep(60*2)  # To be sure we see everyone
        await self.update()


def setup(bot):
    bot.add_cog(Carbonitex(bot))
