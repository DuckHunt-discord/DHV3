# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5

"""

"""
import asyncio
import datetime
import random
import time

import discord
from discord.ext import commands
from prettytable import PrettyTable

from cogs.utils import checks, comm, commons, ducks, prefs, scores
from cogs.utils.commons import _

HOUR = 3600
DAY = 86400


class Exp:
    """Commends to use, spend and give exp."""

    def __init__(self, bot):
        self.bot = bot

    def objectTD(self, channel, target, language, object):
        date_expiration = datetime.datetime.fromtimestamp(scores.getStat(channel, target, object, default=0))
        td = date_expiration - datetime.datetime.now()
        return _("{date} (in {dans_jours}{dans_heures} and {dans_minutes})", language).format(**{
            "date"        : date_expiration.strftime(_('%H:%M:%S le %d/%m', language)),
            "dans_jours"  : _("{dans} days ").format(**{
                "dans": td.days
            }) if td.days else "",
            "dans_heures" : _("{dans} hours").format(**{
                "dans": td.seconds // 3600
            }),
            "dans_minutes": _("{dans} minutes").format(**{
                "dans": (td.seconds // 60) % 60
            })
        })

    @commands.command(pass_context=True)
    @checks.is_not_banned()
    @checks.is_activated_here()
    async def sendexp(self, ctx, target: discord.Member, amount: int):
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        if prefs.getPref(message.server, "user_can_give_exp"):

            if amount <= 0:
                await comm.message_user(message, _(":x: You need to give a positive number for the exp to send", language))
                comm.logwithinfos_message(message, "[sendexp] montant invalide")
                return

            if scores.getStat(message.channel, message.author, "exp") > amount:
                scores.addToStat(message.channel, message.author, "exp", -amount)
                if prefs.getPref(message.server, "tax_on_user_give") > 0:
                    taxes = amount * (prefs.getPref(message.server, "tax_on_user_give") / 100)
                else:
                    taxes = 0
                scores.addToStat(message.channel, target, "exp", amount - taxes)
                await comm.message_user(message, _("You sent {amount} exp to {target} (and paid {taxes} exp of taxes for this transfer) !", language).format(**{
                    "amount": amount - taxes,
                    "target": target.mention,
                    "taxes" : taxes
                }))
                comm.logwithinfos_message(message, "[sendexp] Exp points sent to {target} : {amount} exp recived, and {taxes} exp of transfer taxes percived ".format(**{
                    "amount": amount - taxes,
                    "target": target.mention,
                    "taxes" : taxes
                }))
            else:
                await comm.message_user(message, _("You don't have enough experience points", language))

    @commands.command(pass_context=True)
    @checks.is_not_banned()
    @checks.is_activated_here()
    async def duckstats(self, ctx, target: discord.Member = None):
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        now = int(time.time())
        if not target:
            target = ctx.message.author
        level = scores.getPlayerLevel(message.channel, target)
        x = PrettyTable()
        if scores.getStat(message.channel, target, "canardsTues") > 0:
            ratio = round(scores.getStat(message.channel, target, "exp") / scores.getStat(message.channel, target, "canardsTues"), 4)
        else:
            ratio = _("No duck killed", language)
        x._set_field_names([_("Statistic", language), _("Value", language)])
        x.add_row([_("Ducks killed", language), scores.getStat(message.channel, target, "canardsTues")])
        x.add_row([_("Shots missed", language), scores.getStat(message.channel, target, "tirsManques")])
        x.add_row([_("Shots without ducks", language), scores.getStat(message.channel, target, "tirsSansCanards")])
        x.add_row([_("Best killing time", language), scores.getStat(message.channel, target, "meilleurTemps", default=prefs.getPref(message.server, "time_before_ducks_leave"))])
        x.add_row([_("Bullets in current charger", language), str(scores.getStat(message.channel, target, "balles", default=level["balles"])) + " / " + str(level["balles"])])
        x.add_row([_("Chargers left", language), str(scores.getStat(message.channel, target, "chargeurs", default=level["chargeurs"])) + " / " + str(level["chargeurs"])])
        x.add_row([_("Exp points", language), scores.getStat(message.channel, target, "exp")])
        x.add_row([_("Ratio (exp/ducks killed)", language), ratio])

        x.add_row([_("Current level", language), str(level["niveau"]) + " (" + _(level["nom"], language) + ")"])
        x.add_row([_("Shots accuracy", language), level["precision"]])
        x.add_row([_("Weapon fiability", language), level["fiabilitee"]])
        if scores.getStat(message.channel, target, "graisse", default=0) > int(time.time()):
            x.add_row([_("Object : grease", language), self.objectTD(message.channel, target, language, "graisse")])
        if scores.getStat(message.channel, target, "detecteurInfra", default=0) > int(time.time()):
            x.add_row([_("Object : infrared detector", language), self.objectTD(message.channel, target, language, "detecteurInfra")])
        if scores.getStat(message.channel, target, "silencieux", default=0) > int(time.time()):
            x.add_row([_("Object : silencer", language), self.objectTD(message.channel, target, language, "silencieux")])
        if scores.getStat(message.channel, target, "trefle", default=0) > int(time.time()):
            x.add_row([_("Object : clover {exp} exp", language).format(**{
                "exp": scores.getStat(message.channel, target, "trefle_exp", default=0)
            }), self.objectTD(message.channel, target, language, "trefle")])
        if scores.getStat(message.channel, target, "munExplo", default=0) > int(time.time()):
            x.add_row([_("Object : explosive ammo", language), self.objectTD(message.channel, target, language, "munExplo")])
        elif scores.getStat(message.channel, target, "munAp_", default=0) > int(time.time()):
            x.add_row([_("Object : AP ammo", language), self.objectTD(message.channel, target, language, "munAp_")])
        if scores.getStat(message.channel, target, "mouille", default=0) > int(time.time()):
            x.add_row([_("Effect : wet", language), self.objectTD(message.channel, target, language, "mouille")])

        await comm.message_user(message, _("Statistics of {mention} : \n```{table}```\nhttps://api-d.com/snaps/table_de_progression.html", language).format(**{
            "table"  : x.get_string(),
            "mention": target.mention
        }))

    @commands.command(pass_context=True)
    @checks.is_not_banned()
    @checks.is_activated_here()
    async def top(self, ctx, number_of_scores: int = 10):
        language = prefs.getPref(ctx.message.server, "language")

        if number_of_scores > 200 or number_of_scores < 1:
            await comm.message_user(ctx.message, _(":x: The maximum number of scores that can be shown on a topscores table is 200.", language))
            return

        x = PrettyTable()

        x._set_field_names([_("Rank", language), _("Nickname", language), _("Exp points", language), _("Ducks killed", language)])

        i = 0
        for joueur in scores.topScores(ctx.message.channel):
            i += 1
            if (joueur["canardsTues"] is None) or (joueur["canardsTues"] == 0) or ("canardTues" in joueur == False):
                joueur["canardsTues"] = "AUCUN !"
            if joueur["exp"] is None:
                joueur["exp"] = 0
            x.add_row([i, joueur["name"].replace("`", ""), joueur["exp"], joueur["canardsTues"]])

        await comm.message_user(ctx.message, _(":cocktail: Best scores for #{channel_name} : :cocktail:\n```{table}```", language).format(**{
            "channel_name": ctx.message.channel.name,
            "table"       : x.get_string(end=number_of_scores, sortby=_("Rank", language))
        }), )

    @commands.group(pass_context=True)
    @checks.is_not_banned()
    @checks.is_activated_here()
    async def shop(self, ctx):
        from cogs import shoot
        shoot.Shoot.giveBackIfNeeded(ctx.message.channel, ctx.message.author)
        if not ctx.invoked_subcommand:
            await comm.message_user(ctx.message, ":x: Incorrect syntax : `!shop [item number] [argument if applicable]`")

    @shop.command(pass_context=True, name="1")
    @checks.have_exp(7)
    async def item1(self, ctx):
        """Add a bullet to your weapon (7 exp)
        !shop 1"""
        message = ctx.message
        language = prefs.getPref(message.server, "language")

        if scores.getStat(message.channel, message.author, "balles", default=scores.getPlayerLevel(message.channel, message.author)["balles"]) < scores.getPlayerLevel(message.channel, message.author)["balles"]:

            await comm.message_user(message, _(":money_with_wings: You add a bullet to your weapon for 7 exp points", language))
            scores.addToStat(message.channel, message.author, "balles", 1)
            scores.addToStat(message.channel, message.author, "exp", -7)

        else:
            await comm.message_user(message, _(":champagne: Your charger is full !", language))

    @shop.command(pass_context=True, name="2")
    @checks.have_exp(13)
    async def item2(self, ctx):
        """Add a charger to your weapon (13 exp)
        !shop 2"""
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        if scores.getStat(message.channel, message.author, "chargeurs", default=scores.getPlayerLevel(message.channel, message.author)["chargeurs"]) < scores.getPlayerLevel(message.channel, message.author)["chargeurs"]:
            await comm.message_user(message, _(":money_with_wings: You add a charger to your backpack for 13 exp points.", language))
            scores.addToStat(message.channel, message.author, "chargeurs", 1)
            scores.addToStat(message.channel, message.author, "exp", -13)

        else:
            await comm.message_user(message, _(":champagne: You have enough chargers!", language))

    @shop.command(pass_context=True, name="3")
    @checks.have_exp(15)
    async def item3(self, ctx):
        """Buy AP ammo (15 exp)
        !shop 3"""
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        if scores.getStat(message.channel, message.author, "munAP_", default=0) < time.time():
            await comm.message_user(message, _(":money_with_wings: You purchase AP ammo for your weapon. For the next 24 hours, you will deal double damage to ducks.", language))
            scores.addToStat(message.channel, message.author, "munAP_", int(time.time() + DAY))
            scores.addToStat(message.channel, message.author, "exp", -15)

        else:
            await comm.message_user(message, _(":champagne: You have enough AP ammo for now!", language))

    @shop.command(pass_context=True, name="4")
    @checks.have_exp(25)
    async def item4(self, ctx):
        """Buy explosive ammo (25 exp)
        !shop 4"""
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        if scores.getStat(message.channel, message.author, "munExplo", default=0) < time.time():
            await comm.message_user(message, _(":money_with_wings: You purchase explosive ammo for your weapon. For the next 24 hours, you will deal triple damage to ducks.", language))
            scores.addToStat(message.channel, message.author, "munExplo", int(time.time() + DAY))
            scores.addToStat(message.channel, message.author, "exp", -25)

        else:
            await comm.message_user(message, _(":champagne: You have enough explosive ammo for now!", language))

    @shop.command(pass_context=True, name="5")
    @checks.have_exp(40)
    async def item5(self, ctx):
        """Get back your weapon (40 exp)
        !shop 5"""
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        if scores.getStat(message.channel, message.author, "confisque"):
            await comm.message_user(message, _(":money_with_wings: You take your weapon back for 40 exp points", language))
            scores.addToStat(message.channel, message.author, "confisque", False)
            scores.addToStat(message.channel, message.author, "exp", -40)

        else:
            await comm.message_user(message, _(":champagne: You haven't kill anyone today, you have your weapon, what do you want to buy ? :p", language))

    @shop.command(pass_context=True, name="6")
    @checks.have_exp(8)
    async def item6(self, ctx):
        """Buy grease for your weapon (8 exp)
        !shop 6"""
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        if scores.getStat(message.channel, message.author, "graisse", default=0) < int(time.time()):
            await comm.message_user(message, _(":money_with_wings: You add grease in your weapon to reduce jamming risks by 50% for a day, for only 8 exp points.", language))
            scores.addToStat(message.channel, message.author, "graisse", time.time() + DAY)
            scores.addToStat(message.channel, message.author, "exp", -8)

        else:
            await comm.message_user(message, _(":champagne: Your weapon is perfectly lubricated, no need for more grease", language))

    @shop.command(pass_context=True, name="7")
    async def item7(self, ctx):
        raise NotImplementedError

    @shop.command(pass_context=True, name="8")
    @checks.have_exp(15)
    async def item8(self, ctx):
        """Buy an infrared detector (15 exp)
        !shop 8"""
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        if scores.getStat(message.channel, message.author, "detecteurInfra", default=0) < int(time.time()):
            await comm.message_user(message, _(":money_with_wings: You add an infrared detector to your weapon, that will prevent any waste of ammo for a day. Cost : 15 exp points.", language))
            scores.addToStat(message.channel, message.author, "detecteurInfra", time.time() + DAY)
            scores.addToStat(message.channel, message.author, "exp", -15)

        else:
            await comm.message_user(message, _(":champagne: You do have an infrared detector on your weapon, right ?", language))

    @shop.command(pass_context=True, name="9")
    @checks.have_exp(5)
    async def item9(self, ctx):
        """Buy a silencer (5 exp)
        !shop 9"""
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        if scores.getStat(message.channel, message.author, "silencieux", default=0) < int(time.time()):
            await comm.message_user(message, _(":money_with_wings: You add a silencer to your weapon, no duck will ever be frightened by one of your shots for a day. Cost : 5 exp points, what a good deal !", language))
            scores.addToStat(message.channel, message.author, "silencieux", time.time() + DAY)
            scores.addToStat(message.channel, message.author, "exp", -5)

        else:
            await comm.message_user(message, _(":champagne: You do have a silencer on your weapon, right ?", language))

    @shop.command(pass_context=True, name="10")
    @checks.have_exp(13)
    async def item10(self, ctx):
        """Buy a 4leaf clover (13 exp)
        !shop 10"""
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        if scores.getStat(message.channel, message.author, "clover", default=0) < int(time.time()):
            exp = random.randint(prefs.getPref(message.server, "clover_min_exp"), prefs.getPref(message.server, "clover_max_exp"))
            await comm.message_user(message, _(":money_with_wings: You buy a fresh 4-leaf clover, which will give you {exp} more exp point for the next day. You brought it for 13 exp!", language).format(**{
                "exp": exp
            }))
            scores.setStat(message.channel, message.author, "trefle", int(time.time()) + 86400)
            scores.setStat(message.channel, message.author, "trefle_exp", exp)
            scores.addToStat(message.channel, message.author, "exp", -13)

        else:
            await comm.message_user(message, _(":champagne: You're too lucky, but I don't have any clover left for you today :'(. Too much luck, maybe ??", language))

    @shop.command(pass_context=True, name="11")
    async def item11(self, ctx):
        raise NotImplementedError

    @shop.command(pass_context=True, name="12")
    @checks.have_exp(7)
    async def item12(self, ctx):
        """Buy new clothes, dry ones :p (7 exp)
        !shop 12"""
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        if scores.getStat(message.channel, message.author, "silencieux", default=0) < int(time.time()):
            await comm.message_user(message, _(":money_with_wings: You have some dry clothes on you now. You looks beautiful ! ", language))
            scores.addToStat(message.channel, message.author, "mouille", 0)
            scores.addToStat(message.channel, message.author, "exp", -7)

        else:
            scores.addToStat(message.channel, message.author, "exp", -7)
            await comm.message_user(message, _(":money_with_wings: You brought brand new clothes, for nothing but the fact that you are mostly swag now. :cool:", language))

    @shop.command(pass_context=True, name="13")
    async def item13(self, ctx):
        raise NotImplementedError

    @shop.command(pass_context=True, name="14")
    async def item14(self, ctx):
        raise NotImplementedError

    @shop.command(pass_context=True, name="15")
    async def item15(self, ctx):
        raise NotImplementedError

    @shop.command(pass_context=True, name="16")
    @checks.have_exp(10)
    async def item16(self, ctx, target: discord.Member):
        """ Drop a water bucket on someone (10 exp)
        !shop 16 [target]"""
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        await comm.message_user(message, _(":money_with_wings: You drop a full water bucket on {target}, frocing him to wait 1 hour for his/her clothes to dry before he/she can return hunting", language).format(**{
            "target": target.name
        }))
        scores.setStat(message.channel, target, "mouille", int(time.time()) + 3600)
        scores.addToStat(message.channel, message.author, "exp", -10)

    @shop.command(pass_context=True, name="17")
    @checks.have_exp(14)
    async def item17(self, ctx, target: discord.Member):
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        if scores.getStat(message.channel, target, "sabotee", "-") == "-":
            await comm.message_user(message, _(":ok: {target} weapon is sabotaged... But he don't know it :D (14 exp) !", language).format(**{
                "target": target.name
            }), forcePv=True)
            scores.addToStat(message.channel, message.author, "exp", -14)
            scores.setStat(message.channel, target, "sabotee", message.author.name)
        else:
            await comm.message_user(message, _(":ok: {target} weapon is already sabotaged!", language).format(**{
                "target": target.name
            }), forcePv=True)

    @shop.command(pass_context=True, name="18")
    @checks.have_exp(10)
    async def item18(self, ctx):
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        if scores.getStat(message.channel, message.author, "AssuranceVie", default=0) < int(time.time()):
            await comm.message_user(message, _(":money_with_wings: You buy a life insurence for a week for 10 exp. If you get killed, you will earn half the level of the killer in exp", language))
            scores.setStat(message.channel, message.author, "AssuranceVie", int(time.time()) + DAY * 7)
            scores.addToStat(message.channel, message.author, "exp", -10)

        else:
            await comm.message_user(message, _(":money_with_wings: You are already insured.", language))

    @shop.command(pass_context=True, name="19")
    async def item19(self, ctx):
        raise NotImplementedError

    @shop.command(pass_context=True, name="20")
    @checks.have_exp(8)
    async def item20(self, ctx):
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        await comm.message_user(message, _(":money_with_wings: A duck will appear in the next 10 minutes on the channel, thanks to the decoy of {mention}. He brought it for 8 exp !", language).format(**{
            "mention": message.author.mention
            }))
        scores.addToStat(message.channel, message.author, "exp", -8)
        dans = random.randint(0, 60 * 10)
        await asyncio.sleep(dans)
        await ducks.spawn_duck({
                                   "time": int(time.time()),
                                   "channel": message.channel
                                   })

    @shop.command(pass_context=True, name="21")
    async def item21(self, ctx):
        raise NotImplementedError

    @shop.command(pass_context=True, name="22")
    @checks.have_exp(5)
    async def item22(self, ctx):
        servers = prefs.JSONloadFromDisk("channels.json", default="{}")
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        await comm.message_user(message, _(":money_with_wings: You will be warned when the next duck on #{channel_name} spawns", language).format(**{
            "channel_name": message.channel.name
            }), forcePv=True)
        if message.channel.id in servers[message.server.id]["detecteur"]:
            servers[message.server.id]["detecteur"][message.channel.id].append(message.author.id)
        else:
            servers[message.server.id]["detecteur"][message.channel.id] = [message.author.id]
        prefs.JSONsaveToDisk(servers, "channels.json")
        scores.addToStat(message.channel, message.author, "exp", -5)


    @shop.command(pass_context=True, name="23")
    @checks.have_exp(40)
    async def item23(self, ctx):
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        await comm.message_user(message, _(":money_with_wings: You prepare a mechanical duck on the channel for 50 exp. That's bad, but so funny !", language), forcePv=True)
        scores.addToStat(message.channel, message.author, "exp", -50)
        await asyncio.sleep(75)
        try:
            if prefs.getPref(message.server, "randomize_mechanical_ducks") == 0:
                await self.bot.send_message(message.channel, _("-_-'`'°-_-.-'`'° %__%   *BZAACK*", language))
            elif prefs.getPref(message.server, "randomize_mechanical_ducks") == 1:
                await self.bot.send_message(message.channel, "-_-'`'°-_-.-'`'° %__%    " + _(random.choice(commons.canards_cri), language=language))
            else:
                await self.bot.send_message(message.channel, random.choice(commons.canards_trace) + "  " + random.choice(commons.canards_portrait) + "  " + _(random.choice(commons.canards_cri), language=language))  # ASSHOLE ^^

        except:
            pass


def setup(bot):
    bot.add_cog(Exp(bot))
