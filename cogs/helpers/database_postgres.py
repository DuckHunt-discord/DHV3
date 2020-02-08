from collections import defaultdict
from typing import Optional

import asyncpg as asyncpg

SQL_CREATE_TABLE_CHANNELS = """
        CREATE TABLE "public"."enabled_channels" (
                "discord_channel_id" bigint NOT NULL,
                "discord_guild_id" bigint NOT NULL,
                "enabled" bool NOT NULL,
                PRIMARY KEY ("discord_channel_id")
                );
                """

class Database:
    def __init__(self, bot):
        self.bot = bot
        self.poll: Optional[asyncpg.pool.Pool] = None
        self.caches = {"preferences": {},              # {guild: {pref: value, ...} ...}
                       "players": {},                  # {guild: {user: {category: value, ...}, ...}, ...}
                       "admins": defaultdict(list),    # {guild: [user, ...], ...}
                       "enabled_channels": []}         # [channel, ...]

    async def get_poll(self) -> asyncpg.pool.Pool:
        if not self.poll:
            self.poll = await asyncpg.create_pool('postgresql://duckhunt:duckhunt@localhost/dhv3')

        return self.poll

    async def _migration_populate_channels(self):
        poll = await self.get_poll()
        await poll.execute(SQL_CREATE_TABLE_CHANNELS)
        records = []

        for channel in self.bot.db.database.query("SELECT channel, server, enabled FROM channels"):
            if channel.channel != 0:
                records.append((channel.channel, channel.server, bool(channel.enabled)))

        #return records[:2]

        async with poll.acquire() as conn:
            await conn.copy_records_to_table(table_name="enabled_channels", records=records)





def setup(bot):
    bot.db_pg = Database(bot)
