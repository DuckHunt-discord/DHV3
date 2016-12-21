import asyncio
import random
import time

import discord
from discord.ext import commands

from cogs.utils import comm, commons, prefs, scores
from cogs.utils.comm import logwithinfos
from cogs.utils.commons import _
from .utils import checks


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

    @commands.command(pass_context=True)
    @checks.is_activated_here()
    @checks.is_not_banned()
    async def bang(self, ctx):
        message = ctx.message
        language = prefs.getPref(message.server, "language")

        await self.giveBackIfNeeded(ctx.message)
        if scores.getStat(message.channel, message.author, "mouille", default=0) > int(time.time()):  # Water
            await comm.message_user(message, _("You are not dry, you cant go hunting ! Wait {temps_restant} minutes. ", language).format(**{
                "temps_restant": int((scores.getStat(message.channel, message.author, "mouille", default=0) - int(time.time())) / 60)
            }))
            return

        if scores.getStat(message.channel, message.author, "confisque", default=False):  # No weapon
            await comm.message_user(message, _("You don't have a weapon", language))
            return

        if scores.getStat(message.channel, message.author, "enrayee", default=False):  # Jammed
            await comm.message_user(message, _("Your gun jammed, it must be reloaded to unstuck.", language))
            return

        if scores.getStat(message.channel, message.author, "sabotee", default="-") is not "-":  # Sabotaged
            await comm.message_user(message, _("Your weapon is sabotaged, thank {assaillant} for this bad joke.", language).format(**{
                "assaillant": scores.getStat(message.channel, message.author, "sabotee", default="-")
            }))
            scores.setStat(message.channel, message.author, "enrayee", True)
            scores.setStat(message.channel, message.author, "sabotee", "-")
            return

        if scores.getStat(message.channel, message.author, "balles", default=scores.getPlayerLevel(message.channel, message.author)["balles"]) <= 0:  # No more bullets in charger
            await comm.message_user(message, _("** CHARGER EMPTY ** | Ammunition in the weapon: {balles_actuelles} / {balles_max} | Chargers remaining: {chargeurs_actuels} / {chargeurs_max}", language).format(**{
                "balles_actuelles" : scores.getStat(message.channel, message.author, "balles", default=scores.getPlayerLevel(message.channel, message.author)["balles"]),
                "balles_max"       : scores.getPlayerLevel(message.channel, message.author)["balles"],
                "chargeurs_actuels": scores.getStat(message.channel, message.author, "chargeurs", default=scores.getPlayerLevel(message.channel, message.author)["chargeurs"]),
                "chargeurs_max"    : scores.getPlayerLevel(message.channel, message.author)["chargeurs"]
            }))
            return

        if not random.randint(1, 100) < scores.getPlayerLevel(message.channel, message.author)["fiabilitee"] and not (scores.getStat(message.channel, message.author, "graisse", default=0) > int(time.time())):  # Weapon jammed just now
            await comm.message_user(message, _("Your weapon jammed, reload to unstuck.", language))
            scores.setStat(message.channel, message.author, "enrayee", True)
            return

        current_duck = None

        if commons.ducks_spawned:
            for duck in commons.ducks_spawned:
                if duck["channel"] == message.channel:
                    current_duck = duck
                    break

        if not current_duck and scores.getStat(message.channel, message.author, "detecteurInfra", default=0) > int(time.time()):  # No ducks but infrared detector
            await comm.message_user(message, _("There are no duck here, but the bullet didn't fired because the infrared detector you added to your weapon is doing it's job!", language))
            return

        scores.addToStat(message.channel, message.author, "balles", -1)

        if not current_duck:  # No duck
            await self.sendBangMessage(message, _("Luckily you missed, what were you aiming at exactly? There are no duck here... [missed : -1 xp] [wild shot: -1 xp]", language))
            scores.addToStat(message.channel, message.author, "exp", -2)
            return

        if random.randint(1, 100) < prefs.getPref(message.server, "duck_frighten_chance") and scores.getStat(message.channel, message.author, "silencieux", default=0) < int(time.time()):  # Duck frightened
            try:
                commons.ducks_spawned.remove(current_duck)
                commons.n_ducks_flew += 1
                scores.addToStat(message.channel, message.author, "exp", -1)
                await self.sendBangMessage(message, _("**FLAPP**\tFrightened by so much noise, the duck fled ! CONGRATS ! [missed : -1 xp]", language))
            except ValueError:
                await self.sendBangMessage(message, _("**PIEWW**\tYou missed the duck ! [missed : -1 xp]", language))
            return

        if random.randint(1, 100) > scores.getPlayerLevel(message.channel, message.author)["precision"]:

            if random.randint(1, 100) < prefs.getPref(message.server, "chance_to_kill_on_missed"):  # Missed and shot someone

                scores.addToStat(message.channel, message.author, "exp", -3)
                scores.addToStat(message.channel, message.author, "tirsManques", 1)
                scores.addToStat(message.channel, message.author, "chasseursTues", 1)
                scores.setStat(message.channel, message.author, "confisque", True)

                victim = random.choice(list(message.server.members))
                if victim is not message.author:
                    await self.sendBangMessage(message, _("**BANG**\tYou missed the duck... And shot {player}. ! [missed : -1 xp] [hunting accident : -2 xp] [weapon confiscated]", language).format(**{
                        "player": victim.mention if prefs.getPref(message.server, "killed_mentions") else victim.name
                    }))
                else:
                    await self.sendBangMessage(message, _("**BANG**\tYou missed the duck... but shot yourself. Turn your weapon a little before shooting the next time, maybe ? [missed : -1 xp] [hunting accident : -2 xp] [weapon confiscated]", language))

                if scores.getStat(message.channel, victim, "AssuranceVie", default=0) > int(time.time()):
                    exp = int(scores.getPlayerLevel(message.channel, message.author)["niveau"] / 2)
                    scores.addToStat(message.channel, victim, "exp", exp)
                    await self.bot.send_message(message.channel, str(victim.mention) + _(" > You won {exp} with your life insurance", language).format(**{
                        "exp": exp
                    }))
                return
            else:  # Missed and none was shot
                scores.addToStat(message.channel, message.author, "exp", -1)
                scores.addToStat(message.channel, message.author, "tirsManques", 1)
                await self.sendBangMessage(message, _("**PIEWW**\tYou missed the duck ! [missed : -1 xp]", language))
                return

        if scores.getStat(message.channel, message.author, "munExplo", default=0) > int(time.time()):
            current_duck["SCvie"] -= 3
            vieenmoins = 3
        elif scores.getStat(message.channel, message.author, "munAp_", default=0) > int(time.time()):
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
                await self.sendBangMessage(message, _("That was close, you almost killed the duck, but the other hunter got it first ! [exp -1]", language))
                scores.addToStat(message.channel, message.author, "exp", -1)
                scores.addToStat(message.channel, message.author, "tirsManques", 1)
                return

            exp = prefs.getPref(message.server, "exp_won_per_duck_killed")
            exp += prefs.getPref(message.server, "super_ducks_exp_multiplier") * (current_duck["level"] - 1) * prefs.getPref(message.server, "exp_won_per_duck_killed")
            if scores.getStat(message.channel, message.author, "trefle") >= time.time():
                exp += scores.getStat(message.channel, message.author, "trefle_exp")

            exp = int(exp)
            now = time.time()
            scores.addToStat(message.channel, message.author, "exp", exp)
            scores.addToStat(message.channel, message.author, "canardsTues", 1)
            if current_duck["level"] > 1:
                scores.addToStat(message.channel, message.author, "superCanardsTues", 1)

            await self.sendBangMessage(message, _(":skull_crossbones: **BOUM**\tYou killed the duck in {time} seconds, you are now at a grand total of {total} duck (of which {supercanards} were super-ducks) killed on #{channel}.     \_X<   *COUAC*   [{exp} exp]", language).format(**{
                "time"        : round(now - current_duck["time"], 4),
                "total"       : scores.getStat(message.channel, message.author, "canardsTues"),
                "channel"     : message.channel,
                "exp"         : exp,
                "supercanards": scores.getStat(message.channel, message.author, "superCanardsTues")
            }))
            if scores.getStat(message.channel, message.author, "meilleurTemps", default=prefs.getPref(message.server, "time_before_ducks_leave")) > int(now - current_duck["time"]):
                scores.setStat(message.channel, message.author, "meilleurTemps", round(now - current_duck["time"], 6))
            if prefs.getPref(message.server, "users_can_find_objects"):
                if random.randint(0, 100) < 25:
                    await comm.message_user(message, _("Searching the brushes arround the duck, you find {inutilitee}", language).format(**{
                        "inutilitee": _(random.choice(commons.inutilite), language)
                    }))

        else:  # Duck harmed
            await self.sendBangMessage(message, _(":gun: Duck survived, try again *SUPER DUCK DETECTED* [life : -{vie}]", language).format(**{
                "vie": vieenmoins
            }))
            current_duck["SCvie"] -= vieenmoins

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
            if scores.getStat(message.channel, message.author, "balles", default=scores.getPlayerLevel(message.channel, message.author)["balles"]) > 0:
                return

        if scores.getStat(message.channel, message.author, "balles", default=scores.getPlayerLevel(message.channel, message.author)["balles"]) <= 0:
            if scores.getStat(message.channel, message.author, "chargeurs", default=scores.getPlayerLevel(message.channel, message.author)["chargeurs"]) > 0:
                scores.setStat(message.channel, message.author, "balles", scores.getPlayerLevel(message.channel, message.author)["balles"])
                scores.addToStat(message.channel, message.author, "chargeurs", -1)
                greet = _("You reload your weapon", language)
            else:
                greet = _("You dont have any ammo left !", language)
        else:
            greet = _("You don't need to reload your weapon", language)

        await comm.message_user(message, _("{greet} | Ammo in weapon : {balles_actuelles}/{balles_max} | Chargers left : {chargeurs_actuels}/{chargeurs_max}", language).format(**{
            "greet"            : greet,
            "balles_actuelles" : scores.getStat(message.channel, message.author, "balles", default=scores.getPlayerLevel(message.channel, message.author)["balles"]),
            "balles_max"       : scores.getPlayerLevel(message.channel, message.author)["balles"],
            "chargeurs_actuels": scores.getStat(message.channel, message.author, "chargeurs", default=scores.getPlayerLevel(message.channel, message.author)["chargeurs"]),
            "chargeurs_max"    : scores.getPlayerLevel(message.channel, message.author)["chargeurs"]
        }))


def setup(bot):
    bot.add_cog(Shoot(bot))
