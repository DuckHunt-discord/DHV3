# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5
import json

from cogs.utils import commons


def getPref(server, pref):
    if not hasattr(commons, "servers"):
        servers = JSONloadFromDisk("channels.json")
        commons.servers = servers
    else:
        servers = commons.servers
    try:
        return servers[server.id]["settings"].get(pref, commons.defaultSettings[pref]["value"])
    except KeyError:
        return commons.defaultSettings[pref]


def JSONsaveToDisk(data, filename):
    with open(filename, 'w') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)
    del commons.servers


def JSONloadFromDisk(filename, default="{}", error=False):
    try:
        file = open(filename, 'r')
        data = json.load(file)
        return data
    except IOError:
        if not error:
            file = open(filename, 'w')
            file.write(default)
            file.close()
            return eval(default)
        else:
            raise
