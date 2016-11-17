# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5

"""

"""
import time


async def init():
    from kyoukai import Kyoukai

    from cogs.utils import prefs
    global kyk, API_VERSION
    kyk = Kyoukai("dh_api", debug=False)
    API_VERSION = "Duckhunt API, 0.0.1 ALPHA"

    async def is_channel_activated(channel):
        servers = prefs.JSONloadFromDisk("channels.json")

        try:
            if channel.id in servers[channel.server.id]["channels"]:
                activated = True
            else:
                activated = False
        except KeyError:
            activated = False

        return activated

    async def prepare_resp(resp_payload, code=200, error_msg="OK"):
        resp = {
            "generated_at": int(time.time()),
            "payload"     : resp_payload,
            "error"       : {
                "code"     : code,
                "error_msg": error_msg
            },
            "api_version" : API_VERSION
        }
        return json.dumps(resp), code, {
            "Content-Type": "application/json"
        }
