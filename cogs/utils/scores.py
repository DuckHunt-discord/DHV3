# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5
"""
Discord-duckhunt -- database.py
Communication avec la base de données pour stocker les stats sur les canards"""
# Constants #
import time

import dataset
import discord

from cogs.utils import prefs
from cogs.utils.commons import _
from . import commons

db = dataset.connect('sqlite:///scores.db')


def _gettable(channel):
    server = channel.server
    if prefs.getPref(server, "global_scores"):
        return db[server.id]
    else:
        return db[server.id + "-" + channel.id]

def getChannelTable(channel):
    table = _gettable(channel)
    return table


def updatePlayerInfo(channel, info):
    table = getChannelTable(channel)
    table.upsert(info, ["id_"])


def addToStat(channel, player, stat, value, announce=True):
    if stat == "exp" and prefs.getPref(channel.server, "announce_level_up") and announce:
        ancien_niveau = getPlayerLevel(channel, player)

    dict_ = {
        "name": player.name,
        "id_" : player.id,
        stat  : int(getStat(channel, player, stat)) + value
    }
    updatePlayerInfo(channel, dict_)

    if stat == "exp" and prefs.getPref(channel.server, "announce_level_up") and announce:
        language = prefs.getPref(channel.server, "language")

        embed = discord.Embed(description=_("Level of {player} on #{channel}", language).format(**{
            "player" : player.name,
            "channel": channel.name
        }))

        level = getPlayerLevel(channel, player)
        if ancien_niveau["niveau"] > level["niveau"]:
            embed.title = _("You leveled down!", language)
            embed.colour = discord.Colour.red()
        elif ancien_niveau["niveau"] < level["niveau"]:
            embed.title = _("You leveled up!", language)
            embed.colour = discord.Colour.green()
        else:
            return

        embed.set_thumbnail(url=player.avatar_url if player.avatar_url else commons.bot.user.avatar_url)
        embed.url = 'https://api-d.com/duckhunt/'

        embed.add_field(name=_("Current level", language), value=str(level["niveau"]) + " (" + _(level["nom"], language) + ")")
        embed.add_field(name=_("Previous level", language), value=str(ancien_niveau["niveau"]) + " (" + _(ancien_niveau["nom"], language) + ")")
        embed.add_field(name=_("Shots accuracy", language), value=str(level["precision"]))
        embed.add_field(name=_("Weapon fiability", language), value=str(level["fiabilitee"]))
        embed.add_field(name=_("Exp points", language), value=str(getStat(channel, player, "exp")))
        embed.set_footer(text='DuckHunt V2', icon_url='http://api-d.com/snaps/2016-11-19_10-38-54-q1smxz4xyq.jpg')
        try:
            commons.bot.loop.create_task(commons.bot.send_message(channel, embed=embed))
        except:
            commons.logger.exception("error sending embed, with embed " + str(embed.to_dict()))
            commons.bot.loop.create_task(commons.bot.send_message(channel, _(":warning: Error sending embed, check if the bot have the permission embed_links and try again !", language)))





def setStat(channel, player, stat, value):
    dict_ = {
        "name": player.name,
        "id_" : player.id,
        stat  : value
    }
    updatePlayerInfo(channel, dict_)


def getStat(channel, player, stat, default=0):
    try:
        userDict = getChannelTable(channel).find_one(id_=player.id)
        if userDict[stat] is not None:
            return userDict[stat]
        else:
            setStat(channel, player, stat, default)
            return default

    except:
        try:
            setStat(channel, player, stat, default)
        except:
            pass
        return default


def topScores(channel, stat="exp"):
    table = getChannelTable(channel)

    def defaultInt(s):
        try:
            int(s)
            return s
        except ValueError:
            return 0

        except TypeError:
            return 0

    try:
        return sorted(table.all(), key=lambda k: defaultInt(k[stat]), reverse=True)  # Retourne l'ensemble des joueurs dans une liste par stat
    except:
        return []


def giveBack(player, channel):
    table = _gettable(channel)
    user = getChannelTable(channel).find_one(id_=player.id)
    if not "exp" in user or not user["exp"]:
        user["exp"] = 0
    table.upsert({
        "id_"         : user["id_"],
        "chargeurs"   : getPlayerLevelWithExp(user["exp"])["chargeurs"],
        "confisque"   : False,
        "lastGiveback": int(time.time())
    }, ['id_'])


def getPlayerLevel(channel, player):
    plexp = getStat(channel, player, "exp")
    lvexp = -999999
    numero = 0
    level = commons.levels[numero]

    while lvexp < plexp:
        level = commons.levels[numero]
        if len(commons.levels) > numero + 1:

            lvexp = commons.levels[numero + 1]["expMin"]
            numero += 1
        else:
            return level

    return level


def getPlayerLevelWithExp(exp):
    lvexp = -999999
    numero = 0
    level = commons.levels[numero]

    while lvexp < exp:
        level = commons.levels[numero]
        if len(commons.levels) > numero + 1:

            lvexp = commons.levels[numero + 1]["expMin"]
            numero += 1
        else:
            return level

    return level


def delServerTables(server):
    for table_name in db.tables:
        table_name.split("-")
        if str(table_name[0]) == str(server.id):
            table_ = db.load_table(table_name=table_name)
            table_.drop()


def delChannelTable(channel):
    table = _gettable(channel)
    table.drop()
