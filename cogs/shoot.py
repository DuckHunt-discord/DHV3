# -*- coding: utf-8 -*-
import asyncio
import random
import time

import discord
from discord.ext import commands

from cogs.utils import checks, comm, commons, prefs, scores
from cogs.utils.comm import logwithinfos
from cogs.utils.commons import _


# to expose to the eval command


class Shoot:
    """Basic commands for shooting and reloading a weapon"""

    def __init__(self, bot):
        self.bot = bot

    async def giveBackIfNeeded(self, message):
        channel = message.channel
        player = message.author
        lastGB = int(scores.getStat(channel, player, "lastGiveback", default=int(time.time())))
        if int(lastGB / 86400) != int(int(time.time()) / 86400):
            await logwithinfos(channel, player, "GiveBack  > LastGB :" + str(lastGB) + " / 86400 = " + str(int(lastGB / 86400)))
            await logwithinfos(channel, player, "GiveBack  > Now : " + str(int(time.time())) + " / 86400 = " + str(int(int(time.time()) / 86400)))
            await logwithinfos(channel, player, "Giveback des armes et chargeurs")
            scores.giveBack(player=player, channel=channel)
            scores.addToStat(channel, player, "givebacks", 1)
        else:
            # logger.debug("Pas besoin de passer à l'armurerie")
            return

    async def sendBangMessage(self, message: discord.Message, string: str):
        lag = prefs.getPref(message.server, "bang_lag")
        if lag > 0:
            tmp = await self.bot.send_message(message.channel, str(message.author.mention) + " > BANG")
            await asyncio.sleep(lag)
            await self.bot.edit_message(tmp, str(message.author.mention) + " > " + string)

        else:
            await comm.message_user(message, string)

    @commands.command(pass_context=True, aliases=["pan", "shoot"])
    @checks.is_activated_here()
    @checks.is_not_banned()
    async def bang(self, ctx):
        message = ctx.message
        channel = message.channel
        author = message.author

        language = prefs.getPref(message.server, "language")
        await self.giveBackIfNeeded(message)

        if scores.getStat(channel, author, "mouille") > int(time.time()):  # Water
            await comm.message_user(message, _("You are not dry, you cant go hunting ! Wait {temps_restant} minutes. ", language).format(**{
                "temps_restant": int((scores.getStat(channel, author, "mouille") - int(time.time())) / 60)
            }))
            scores.addToStat(channel, author, "shoots_tried_while_wet", 1)
            return

        if scores.getStat(channel, author, "confisque", default=False):  # No weapon
            await comm.message_user(message, _("You don't have a weapon", language))
            scores.addToStat(channel, author, "shoots_without_weapon", 1)
            return

        if scores.getStat(channel, author, "enrayee", default=False):  # Jammed
            await comm.message_user(message, _("Your weapon is jammed, it must be reloaded to unstuck it.", language))
            scores.addToStat(channel, author, "shoots_with_jammed_weapon", 1)
            return

        if scores.getStat(channel, author, "sabotee", default="-") is not "-":  # Sabotaged
            await comm.message_user(message, _("Your weapon is sabotaged, thank {assaillant} for this bad joke.", language).format(**{
                "assaillant": scores.getStat(channel, author, "sabotee", default="-")
            }))
            scores.addToStat(channel, author, "shoots_sabotaged", 1)
            scores.setStat(channel, author, "enrayee", True)
            scores.setStat(channel, author, "sabotee", "-")
            return

        if scores.getStat(channel, author, "balles", default=scores.getPlayerLevel(channel, author)["balles"]) <= 0:  # No more bullets in charger
            await comm.message_user(message, _("** CHARGER EMPTY ** | Ammunition in the weapon: {balles_actuelles} / {balles_max} | Chargers remaining: {chargeurs_actuels} / {chargeurs_max}", language).format(**{
                "balles_actuelles" : scores.getStat(channel, author, "balles", default=scores.getPlayerLevel(channel, author)["balles"]),
                "balles_max"       : scores.getPlayerLevel(channel, author)["balles"],
                "chargeurs_actuels": scores.getStat(channel, author, "chargeurs", default=scores.getPlayerLevel(channel, author)["chargeurs"]),
                "chargeurs_max"    : scores.getPlayerLevel(channel, author)["chargeurs"]
            }))
            scores.addToStat(channel, author, "shoots_without_bullets", 1)
            return

        fiabilite = scores.getPlayerLevel(channel, author)["fiabilitee"]

        if scores.getStat(channel, author, "sand", default=False):
            fiabilite /= 2
            scores.setStat(channel, author, "sand", False)

        if not random.randint(1, 100) < fiabilite and not (scores.getStat(channel, author, "graisse") > int(time.time())):  # Weapon jammed just now
            await comm.message_user(message, _("Your weapon is jammed, reload to unstuck it.", language))
            scores.addToStat(channel, author, "shoots_jamming_weapon", 1)
            scores.setStat(channel, author, "enrayee", True)
            return

        current_duck = None

        if commons.ducks_spawned:
            for duck in commons.ducks_spawned:
                if duck["channel"] == channel:
                    current_duck = duck
                    break

        if not current_duck and scores.getStat(channel, author, "detecteurInfra") > int(time.time()) and scores.getStat(channel, author, "detecteur_infra_shots_left") > 0:  # No ducks but infrared detector
            await comm.message_user(message, _("There isn't any duck in here, but the bullet wasn't fired because the infrared detector you added to your weapon is doing it's job!", language))
            scores.addToStat(channel, author, "shoots_infrared_detector", 1)
            scores.addToStat(channel, author, "detecteur_infra_shots_left", -1)
            return

        scores.addToStat(channel, author, "balles", -1)
        scores.addToStat(channel, author, "shoots_fired", 1)

        if not current_duck:  # No duck
            await self.sendBangMessage(message, _("Luckily you missed, what were you aiming at exactly? There isn't any duck in here... [missed : -1 xp] [wild shot: -1 xp]", language))
            scores.addToStat(channel, author, "exp", -2)
            scores.addToStat(channel, author, "shoots_no_duck", 1)
            return

        if random.randint(1, 100) < prefs.getPref(message.server, "duck_frighten_chance") and scores.getStat(channel, author, "silencieux") < int(time.time()):  # Duck frightened
            try:
                commons.ducks_spawned.remove(current_duck)
                commons.n_ducks_flew += 1
                scores.addToStat(channel, author, "exp", -1)
                await self.sendBangMessage(message, _("**FLAPP**\tFrightened by so much noise, the duck fled ! CONGRATS ! [missed : -1 xp]", language))
                scores.addToStat(channel, author, "shoots_frightened", 1)
            except ValueError:
                await self.sendBangMessage(message, _("**PIEWW**\tYou missed the duck ! [missed : -1 xp]", language))
                scores.addToStat(channel, author, "shoots_missed", 1)
            return

        if scores.getStat(channel, author, "dazzled", True):
            accuracy = 200  # 50% moins de chance de toucher

            scores.setStat(channel, author, "dazzled", False)
        else:
            accuracy = 100

        precision = scores.getPlayerLevel(channel, author)["precision"]
        sight = scores.getStat(channel, author, "sight")
        if sight:
            precision += (100 - precision) / 3
            scores.setStat(channel, author, "sight", sight - 1)

        if random.randint(1, accuracy) > precision * prefs.getPref(message.server, "multiplier_miss_chance") :
            if random.randint(1, 100) < prefs.getPref(message.server, "chance_to_kill_on_missed"):  # Missed and shot someone
                scores.addToStat(channel, author, "exp", -3)
                scores.addToStat(channel, author, "shoots_missed", 1)
                scores.addToStat(channel, author, "killed_players", 1)
                scores.setStat(channel, author, "confisque", True)

                memberlist = scores.getChannelPlayers(channel, columns=['shoots_fired'])
                victim = None
                while not victim:
                    victim = random.choice(memberlist)
                    while not checks.is_player_check(victim):
                        memberlist.remove(victim)
                        victim = random.choice(memberlist)

                    victim = message.server.get_member(str(victim['id_']))

                if victim is not author:
                    await self.sendBangMessage(message, _("**BANG**\tYou missed the duck... And shot {player} ! [missed : -1 xp] [hunting accident : -2 xp] [weapon confiscated]", language).format(**{
                        "player": victim.mention if prefs.getPref(message.server, "killed_mentions") else victim.name
                    }))
                else:
                    await self.sendBangMessage(message, _("**BANG**\tYou missed the duck... but shot yourself. Turn your weapon a little before shooting the next time, maybe ? [missed : -1 xp] [hunting accident : -2 xp] [weapon confiscated]", language))
                    scores.addToStat(channel, author, "self_killing_shoots", 1)

                if scores.getStat(channel, victim, "life_insurance") > int(time.time()):
                    exp = int(scores.getPlayerLevel(channel, author)["niveau"] / 2)
                    scores.addToStat(channel, victim, "exp", exp)
                    await self.bot.send_message(channel, str(victim.mention) + _(" > You won {exp} with your life insurance", language).format(**{
                        "exp": exp
                    }))
                    scores.addToStat(channel, victim, "life_insurence_rewards", 1)
                return
            else:  # Missed and none was shot
                scores.addToStat(channel, author, "exp", -1)
                scores.addToStat(channel, author, "shoots_missed", 1)
                await self.sendBangMessage(message, _("**PIEWW**\tYou missed the duck ! [missed : -1 xp]", language))
                return

        if scores.getStat(channel, author, "explosive_ammo") > int(time.time()):
            current_duck["SCvie"] -= 3
            vieenmoins = 3
        elif scores.getStat(channel, author, "ap_ammo") > int(time.time()):
            current_duck["SCvie"] -= 2
            vieenmoins = 2
        else:
            current_duck["SCvie"] -= 1
            vieenmoins = 1

        if current_duck["SCvie"] <= 0:  # Duck killed
            try:
                commons.ducks_spawned.remove(current_duck)
                commons.n_ducks_killed += 1
            except ValueError:
                await self.sendBangMessage(message, _("That was close, you almost killed the duck, but the other hunter got it first ! [missed : -1 xp]", language))
                scores.addToStat(channel, author, "exp", -1)
                scores.addToStat(channel, author, "shoots_missed", 1)
                scores.addToStat(channel, author, "shoots_almost_killed", 1)
                return

            exp = prefs.getPref(message.server, "exp_won_per_duck_killed")
            exp += prefs.getPref(message.server, "super_ducks_exp_multiplier") * (current_duck["level"] - 1) * prefs.getPref(message.server, "exp_won_per_duck_killed")
            if scores.getStat(channel, author, "trefle") >= time.time():
                toadd = scores.getStat(channel, author, "trefle_exp")
                exp += toadd
                scores.addToStat(channel, author, "exp_won_with_clover", toadd)

            exp = int(exp)
            now = time.time()
            scores.addToStat(channel, author, "exp", exp)
            scores.addToStat(channel, author, "killed_ducks", 1)
            if current_duck["level"] > 1:
                scores.addToStat(channel, author, "killed_super_ducks", 1)

            await self.sendBangMessage(message, _(":skull_crossbones: **BOUM**\tYou killed the duck in {time} seconds, you are now at a grand total of {total} ducks (of which {supercanards} were super-ducks) killed on #{channel}.     \_X<   *COUAC*   [{exp} exp]", language).format(**{
                "time"        : round(now - current_duck["time"], 4),
                "total"       : scores.getStat(channel, author, "killed_ducks"),
                "channel"     : channel,
                "exp"         : exp,
                "supercanards": scores.getStat(channel, author, "killed_super_ducks")
            }))
            if scores.getStat(channel, author, "best_time", default=prefs.getPref(message.server, "time_before_ducks_leave")) > int(now - current_duck["time"]):
                scores.setStat(channel, author, "best_time", round(now - current_duck["time"], 6))
            if prefs.getPref(message.server, "users_can_find_objects"):
                rand = random.randint(0, 1000)
                HOUR = 3600
                DAY = 86400

                if rand <= 50:
                    scores.addToStat(channel, author, "trashFound", 1)
                    await comm.message_user(message, _("While searching the bushes around the duck, you found **{inutilitee}**", language).format(**{
                        "inutilitee": _(random.choice(commons.inutilite), language)
                    }))

                elif rand <= 54:
                    scores.setStat(message.channel, message.author, "explosive_ammo", int(time.time() + DAY))
                    scores.addToStat(message.channel, message.author, "found_explosive_ammo", 1)
                    await comm.message_user(message, _("While searching the bushes around the duck, you found **a box of explosive ammo**", language))

                elif rand <= 60:
                    scores.setStat(message.channel, message.author, "explosive_ammo", int(time.time() + DAY / 4))
                    scores.addToStat(message.channel, message.author, "found_almost_empty_explosive_ammo", 1)
                    await comm.message_user(message, _("While searching the bushes around the duck, you found **a almost empty box of explosive ammo**", language))

                elif rand <= 63:
                    scores.addToStat(message.channel, message.author, "found_chargers", 1)

                    if scores.getStat(message.channel, message.author, "chargeurs", default=scores.getPlayerLevel(message.channel, message.author)["chargeurs"]) < scores.getPlayerLevel(message.channel, message.author)["chargeurs"]:
                        scores.addToStat(message.channel, message.author, "chargeurs", 1)
                        await comm.message_user(message, _("While searching the bushes around the duck, you found **a full charger**", language))
                    else:
                        scores.addToStat(message.channel, message.author, "found_chargers_not_taken", 1)
                        await comm.message_user(message, _("While searching the bushes around the duck, you found **a full charger**. You left it there, cause your backpack is full.", language))
                elif rand <= 70:
                    scores.addToStat(message.channel, message.author, "found_bullets", 1)
                    if scores.getStat(message.channel, message.author, "balles", default=scores.getPlayerLevel(message.channel, message.author)["balles"]) < scores.getPlayerLevel(message.channel, message.author)["balles"]:
                        scores.addToStat(message.channel, message.author, "balles", 1)
                        await comm.message_user(message, _("While searching the bushes around the duck, you found **a bullet**", language))

                    else:  # Shouldn't happen but we never know...
                        await comm.message_user(message, _("While searching the bushes around the duck, you found **a bullet**. You left it there, cause your have enough of them in your charger.", language))
                        scores.addToStat(message.channel, message.author, "found_bullets_not_taken", 1)

        else:  # Duck harmed
            await self.sendBangMessage(message, _(":gun: Duck survived, try again *SUPER DUCK DETECTED* [life : -{vie}]", language).format(**{
                "vie": vieenmoins
            }))
            current_duck["SCvie"] -= vieenmoins
            scores.addToStat(channel, author, "shoots_harmed_duck", 1)

    @commands.command(pass_context=True)
    @checks.is_activated_here()
    @checks.is_not_banned()
    async def reload(self, ctx):
        await self.giveBackIfNeeded(ctx.message)
        message = ctx.message
        language = prefs.getPref(message.server, "language")

        if scores.getStat(message.channel, message.author, "confisque", default=False):
            await comm.message_user(message, _("Your weapon had been confiscated", language))
            return
        if scores.getStat(message.channel, message.author, "enrayee", default=False):
            await comm.message_user(message, _("You unstuck your weapon.", language))
            scores.setStat(message.channel, message.author, "enrayee", False)
            # TODO : simplifier
            if scores.getStat(message.channel, message.author, "balles", default=scores.getPlayerLevel(message.channel, message.author)["balles"]) > 0:
                return

        if scores.getStat(message.channel, message.author, "balles", default=scores.getPlayerLevel(message.channel, message.author)["balles"]) <= 0:
            if scores.getStat(message.channel, message.author, "chargeurs", default=scores.getPlayerLevel(message.channel, message.author)["chargeurs"]) > 0:
                scores.setStat(message.channel, message.author, "balles", scores.getPlayerLevel(message.channel, message.author)["balles"])
                scores.addToStat(message.channel, message.author, "chargeurs", -1)
                scores.addToStat(message.channel, message.author, "reloads", 1)
                greet = _("You reload your weapon", language)
            else:
                greet = _("You dont have any ammo left !", language)
                scores.addToStat(message.channel, message.author, "reloads_without_chargers", 1)
        else:
            greet = _("You don't need to reload your weapon", language)
            scores.addToStat(message.channel, message.author, "unneeded_reloads", 1)

        await comm.message_user(message, _("{greet} | Ammo in weapon : {balles_actuelles}/{balles_max} | Chargers left : {chargeurs_actuels}/{chargeurs_max}", language).format(**{
            "greet"            : greet,
            "balles_actuelles" : scores.getStat(message.channel, message.author, "balles", default=scores.getPlayerLevel(message.channel, message.author)["balles"]),
            "balles_max"       : scores.getPlayerLevel(message.channel, message.author)["balles"],
            "chargeurs_actuels": scores.getStat(message.channel, message.author, "chargeurs", default=scores.getPlayerLevel(message.channel, message.author)["chargeurs"]),
            "chargeurs_max"    : scores.getPlayerLevel(message.channel, message.author)["chargeurs"]
        }))


def setup(bot):
    bot.add_cog(Shoot(bot))
