# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5

"""

"""
import asyncio
import datetime
import os
import socket

import plotly.graph_objs as go
import plotly.plotly as py
import plotly.tools as tls
import psutil

from cogs.utils import commons
from cogs.utils.commons import  _

#tls.set_credentials_file(username='-', api_key='-')


#stream_ids = ["-", "-", "-", "-"]
stream_ids = tls.get_credentials_file()['stream_ids']


async def create_stream(name, title, points=60*60, mode="overwrite"):
    # Make a figure object
    stream_id = stream_ids.pop()
    fig = go.Figure(data=go.Data([go.Scatter(
            x=[],
            y=[],
            mode='lines+markers',
            stream=go.Stream(
                    token=stream_id,  # link stream id to 'token' key
                    maxpoints=points      # keep a max of 900 pts (15 min) on screen
            )         # (!) embed stream id, 1 per trace
    )]), layout= go.Layout(title=title))

    # Send fig to Plotly, initialize streaming plot, open new tab
    py.plot(fig, filename=name,fileopt=mode, auto_open=False)

    # We will provide the stream link object the same token that's associated with the trace we wish to stream to
    s = py.Stream(stream_id)

    # We then open a connection
    try:
        s.open()
    except socket.error:
        commons.logger.error(_("Error sending heartbeat"))
        raise
    return s


async def update_servers(servers_graph):
    x = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    y = len(commons.bot.servers)
    servers_graph.write(dict(x=x, y=y))
    #commons.logger.debug("<3 HEARTBEAT SERVERS <3")

async def update_channels(activated_channels_graph):
    x = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    y = len(commons.ducks_planned)
    activated_channels_graph.write(dict(x=x, y=y))
    #commons.logger.debug("<3 HEARTBEAT CHANNELS <3")

async def update_memory(mem_graph):
    x = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    y = round(psutil.Process(os.getpid()).memory_info()[0] / 2. ** 30 * 1000, 5)
    mem_graph.write(dict(x=x, y=y))
    #commons.logger.debug("<3 HEARTBEAT MEMORY <3")

async def update_users(users_graph):
    x = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    y = 0
    for server in commons.bot.servers:
        y += server.member_count
    users_graph.write(dict(x=x, y=y))
    #commons.logger.debug("<3 HEARTBEAT USERS <3")

async def update_ducks_dest():
    labels=['Ducks killed','Ducks bored']

    values=[commons.n_ducks_killed,commons.n_ducks_flew]

    py.plot([go.Pie(labels=labels,values=values)], filename="Ducks Dest",fileopt="overwrite", auto_open=False)

async def update_ducks(ducks_graph):
    x = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    y = len(commons.ducks_spawned)
    ducks_graph.write(dict(x=x, y=y))

async def analytics_loop():
    try:
        await commons.bot.wait_until_ready()
        await asyncio.sleep(120) # Wait for the cache to be populated, plus don't spam the plotly api if we restart frequently
        commons.logger.debug("[analytics] Creating graphs")
        mem_graph = await create_stream("mem_used", "Memory used in mb", mode="append")
        activated_channels_graph = await create_stream("active_channels", "Channels activated", mode="extend")
        servers_graph = await create_stream("connected_servers", "Number of servers seen by the bot", mode="extend")
        users_graph = await create_stream("number_users", "Number of users", mode="extend")
        ducks_graph = await create_stream("number_ducks", "Number of ducks spawned")

        commons.logger.debug("[analytics] HEARTBEATs STARTED")
        await update_servers(servers_graph)
        await update_channels(activated_channels_graph)
        await update_memory(mem_graph)
        await update_users(users_graph)
        await update_ducks_dest()
        await update_ducks(ducks_graph)

        i = 0
        while True:
            i += 1


            # Current time on x-axis, random numbers on y-axis


            ## MEM GRAPH UPDATE
            if i % 60 == 0:
                await update_servers(servers_graph)
                await update_ducks_dest()

            if i % 30 == 0:
                await update_channels(activated_channels_graph)

            if i % 15 == 0:
                await update_memory(mem_graph)

            if i % 10 == 0:
                await update_users(users_graph)
                await update_ducks(ducks_graph)

            await asyncio.sleep(60)
    except:
        commons.logger.exception("")
        raise

