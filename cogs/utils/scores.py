# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5
"""
Discord-duckhunt -- database.py
Communication avec la base de données pour stocker les stats sur les canards"""

# Constants #
import time
import sqlite3
import discord

from mysql import connector
from cogs.utils import prefs, checks, commons
from cogs.utils.commons import _, credentials

db = connector.connect(host=credentials['mysql_host'], port=credentials['mysql_port'], user=credentials['mysql_user'], password=credentials['mysql_pass'], database=credentials['mysql_db'], charset='utf8mb4', collation='utf8mb4_unicode_ci')
sql = db.cursor(buffered=True, dictionary=True)

def getChannelId(channel):
    server = channel.server
    sql.execute("SELECT id FROM channels WHERE server = %(server)s AND channel = %(channel)s", {
        'server': int(server.id),
        'channel': (0 if prefs.getPref(server, "global_scores") else int(channel.id))
    })

    return sql.fetchone()['id']


def getChannelPlayers(channel, columns=['*'], match_id=None):
    """Retourne une liste composée de dicts correspondant aux joueurs et contenant leurs stats (gère automatiquement le global_scores).

    Paramètres :
    channel -- obligatoire, de type discord.Channel
    columns -- facultatif, pour spécifier les stats à retourner (list).
            Retournera toujours l'id du joueur, si non spécifié
            retourne tout. NE JAMAIS PASSER DE DONNEES ENTREES
            PAR UN UTILISATEUR DANS CE PARAMETRE.
    match_id -- facultatif, pour spécifier l'id d'un joueur.
            Si utilisé, la fonction retournera une liste ne
            contenant qu'une seule entrée, correspondant au
            joueur (sur le channel spécifié).
    """

    channel_id = getChannelId(channel)
    data = {'channel_id': channel_id}

    cond = ''
    if match_id:
        data.update({'match_id': match_id})
        cond = " AND id_ = %(match_id)s"

    if not columns[0] is '*':
        columns.insert(0, 'id_')

    sql.execute("SELECT {columns} FROM players WHERE channel_id = %(channel_id)s{cond}".format(columns=', '.join(columns), cond=cond), data)
    return sql.fetchall()

def addToStat(channel, player, stat, value, announce=True):
    if stat == "exp" and prefs.getPref(channel.server, "announce_level_up") and announce:
        ancien_niveau = getPlayerLevel(channel, player)

    setStat(channel, player, stat, int(getStat(channel, player, stat)) + value)

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
    """Définit la valeur d'une stat d'un joueur. Ne pas passer de valeurs entrées par un user via le paramètre stat."""
    sql.execute("INSERT INTO players (id_, name, channel_id, {stat}) VALUES (%(id)s, %(name)s, %(channel_id)s, %(value)s) ON DUPLICATE KEY UPDATE name = %(name)s, {stat} = %(value)s".format(stat=stat), {
        'id': player.id,
        'name': player.name,
        'channel_id': getChannelId(channel),
        'value': value
    })
    db.commit()


def getStat(channel, player, stat, default=0):
    try:
        userDict = getChannelPlayers(channel, columns=[stat], match_id=player.id)[0]
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

def topScores(channel, stat='exp'):
    table = getChannelPlayers(channel, columns=['name', 'killed_ducks', stat])
    players_list = []

    for player in table:
        if checks.is_player_check(player):
            players_list.append(player)
            # print(str(player["name"]) + " | " + str(player["exp"]) + "|" +  str(player["killed_ducks"]))

    try:
        return sorted(players_list, key=lambda k: (k.get(stat, 0) or 0), reverse=True)  # Retourne l'ensemble des joueurs dans une liste par stat
    except:
        return []


def giveBack(player, channel):
    exp = getStat(channel, player, 'exp')

    sql.execute("INSERT INTO players (id_, channel_id, chargeurs, confisque, lastGiveback) VALUES (%(id)s, %(channel_id)s, %(chargeurs)s, %(confisque)s, %(lastGiveback)s) ON DUPLICATE KEY UPDATE chargeurs = %(chargeurs)s, confisque = %(confisque)s, lastGiveback = %(lastGiveback)s", {
        'id': player.id,
        'channel_id': getChannelId(channel),
        'chargeurs': getPlayerLevelWithExp(exp)["chargeurs"],
        'confisque': False,
        'lastGiveback': int(time.time())
    })
    db.commit()


def getPlayerLevel(channel, player):
    plexp = getStat(channel, player, "exp")
    return getPlayerLevelWithExp(plexp)


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


def delServerPlayers(server=None, sid=None):
    if not sid:
        sid = server.id

    sql.execute("SELECT * FROM channels WHERE server = %(server)s", {'server': sid})
    channels = sql.fetchall()

    for channel in channels:
        sql.execute("DELETE FROM players WHERE channel_id = %(channel_id)s", {'channel_id': channel['id']})

    sql.execute("DELETE FROM channels WHERE server = %(server)s", {'server': sid})
    db.commit()


def delChannelPlayers(channel):
    sql.execute("DELETE FROM players WHERE channel_id = %(channel_id)s", {'channel_id': getChannelId(channel)})
    sql.execute("DELETE FROM channels WHERE server = %(server)s AND channel = %(channel)s", {'server': channel.server.id, 'channel': channel.id})
    db.commit()


# def freeze():
#     for table in db.tables:
#         print("ok")
#         dataset.freeze(db[table], format='json', filename='./bck/' + str(table) + '.json')
