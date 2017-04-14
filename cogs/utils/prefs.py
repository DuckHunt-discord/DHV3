# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5
import json

from cogs.utils import commons

cache = False


def getPref(server, pref):
    if not cache or not hasattr(commons, "servers"):
        servers = JSONloadFromDisk("channels.json")
        commons.servers = servers
    else:
        servers = commons.servers
    try:
        return servers[server.id]["settings"].get(pref, commons.defaultSettings[pref]["value"])
    except KeyError:
        return commons.defaultSettings[pref]["value"]


def setPref(server, pref, value=None, force=False):
    if not cache or not hasattr(commons, "servers"):
        servers = JSONloadFromDisk("channels.json")
        commons.servers = servers
    else:
        servers = commons.servers

    if value is not None:

        if not "settings" in servers[server.id]:
            servers[server.id]["settings"] = {}
        try:
            # print(commons.defaultSettings[pref]["type"](value))
            if "min" in commons.defaultSettings[pref].keys():
                if commons.defaultSettings[pref]["type"](value) < commons.defaultSettings[pref]["min"]:
                    return False

            if "max" in commons.defaultSettings[pref].keys():
                if commons.defaultSettings[pref]["type"](value) > commons.defaultSettings[pref]["max"]:
                    return False

            servers[server.id]["settings"][pref] = commons.defaultSettings[pref]["type"](value)

        except ValueError:
            if force:
                servers[server.id]["settings"][pref] = value
            else:
                return False
    else:
        if not "settings" in servers[server.id]:
            return True
        if pref in servers[server.id]["settings"]:
            servers[server.id]["settings"].pop(pref)

    JSONsaveToDisk(servers, "channels.json")
    return True


def JSONsaveToDisk(data, filename):
    with open(filename, 'w') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=4)
    if hasattr(commons, "servers"):
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
