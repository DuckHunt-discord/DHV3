# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5

"""

"""
import asyncio
import datetime
import sys

import os
import psutil
from cogs.utils import commons

CSV_root = os.path.dirname(os.path.realpath(sys.argv[0])) + "/csv/"


async def get_date():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M')


async def csv_write(file, x, y):
    with open(CSV_root + file, "a") as f:
        f.write("{x},{y}\n".format(x=x, y=y))


async def update_servers():
    x = await get_date()
    y = len(commons.bot.servers)
    await csv_write("servers.csv", x, y)
    commons.logger.debug("Updating server analytics")


async def update_channels():
    x = await get_date()
    y = len(commons.ducks_planned)
    await csv_write("channels.csv", x, y)
    commons.logger.debug("Updating channels analytics")


async def update_memory():
    x = await get_date()
    y = round(psutil.Process(os.getpid()).memory_info()[0] / 2. ** 30 * 1000, 5)
    await csv_write("memory.csv", x, y)
    commons.logger.debug("Updating memory analytics")


async def update_users():
    x = await get_date()
    y = 0
    for server in commons.bot.servers:
        for member in server.members:
            if not member.bot:
                y += 1
    await csv_write("users.csv", x, y)
    commons.logger.debug("Updating users analytics")


async def update_ducks():
    x = await get_date()
    y = len(commons.ducks_spawned)
    await csv_write("ducks.csv", x, y)
    commons.logger.debug("Updating ducks analytics")

async def analytics_loop():
    try:
        await commons.bot.wait_until_ready()  # Wait for the bot to be operational
        await asyncio.sleep(60)  # It might not be the right time to do that. I've seen 0 channels logged, even after on_ready...

        commons.logger.debug("[analytics] HEARTBEATs STARTED")
        await update_servers()
        await update_channels()
        await update_memory()
        await update_users()
        await update_ducks()

        i = 0
        while True:
            i += 1

            # Current time on x-axis, random numbers on y-axis

            if i % 6 == 0:
                await update_servers()

            if i % 3 == 0:
                await update_channels()

            if i % 1 == 0:
                await update_memory()
                await update_users()
                await update_ducks()

            await asyncio.sleep(70)
    except:
        commons.logger.exception("")
        raise

