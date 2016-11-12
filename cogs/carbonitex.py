import json
import logging

import aiohttp
from .utils import commons
log = logging.getLogger()

DISCORD_BOTS_API = 'https://bots.discord.pw/api'


class Carbonitex:
    """Cog for updating  bots.discord.pw bot information."""

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    def __unload(self):
        # pray it closes
        self.bot.loop.create_task(self.session.close())

    async def update(self):

        payload = json.dumps({
            'server_count': len(self.bot.servers)
        })

        headers = {
            'authorization': self.bot.bots_key,
            'content-type' : 'application/json'
        }

        url = '{0}/bots/{1.user.id}/stats'.format(DISCORD_BOTS_API, self.bot)
        async with self.session.post(url, data=payload, headers=headers) as resp:
            commons.logger.info('DBots statistics returned {0.status} for {1}'.format(resp, payload))

    async def on_server_join(self, server):
        await self.update()

    async def on_server_remove(self, server):
        await self.update()

    async def on_ready(self):
        await self.update()


def setup(bot):
    bot.add_cog(Carbonitex(bot))
