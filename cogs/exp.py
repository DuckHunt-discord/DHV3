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
            "date"        : date_expiration.strftime(_('%m/%d at %H:%M:%S', language)),
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
    async def resetbesttime(self, ctx):
        message = ctx.message
        scores.setStat(message.channel, message.author, "meilleurTemps", prefs.getPref(message.server, "time_before_ducks_leave"))
        await comm.message_user(message, _(":ok: Your best time was reset.", prefs.getPref(message.server, "language")))
    @commands.command(pass_context=True)
    @checks.is_not_banned()
    @checks.is_activated_here()
    async def sendexp(self, ctx, target: discord.Member, amount: int):
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        if prefs.getPref(message.server, "user_can_give_exp"):
            if scores.getStat(message.channel, message.author, "confisque", default=False):  # No weapon
                await comm.message_user(message, _(":x: To prevent abuse, you can't send exp when you don't have a weapon.", language))
                return

            if amount <= 0:
                await comm.message_user(message, _(":x: You need to give a positive number for the exp to send", language))
                await comm.logwithinfos_message(message, "[sendexp] montant invalide")
                return

            if scores.getStat(message.channel, message.author, "exp") > amount:
                scores.addToStat(message.channel, message.author, "exp", -amount)
                if prefs.getPref(message.server, "tax_on_user_give") > 0:
                    taxes = amount * (prefs.getPref(message.server, "tax_on_user_give") / 100)
                else:
                    taxes = 0
                try:
                    scores.addToStat(message.channel, target, "exp", amount - taxes)
                except OverflowError:
                    await comm.message_user(ctx.message, _("Congratulations, you sent / gave more experience than the maximum number I'm able to store.",  language))
                    return
                await comm.message_user(message, _("You sent {amount} exp to {target} (and paid {taxes} exp of taxes for this transfer) !", language).format(**{
                    "amount": amount - taxes,
                    "target": target.mention,
                    "taxes" : taxes
                }))
                await comm.logwithinfos_message(message, "[sendexp] Exp points sent to {target} : {amount} exp recived, and {taxes} exp of transfer taxes percived ".format(**{
                    "amount": amount - taxes,
                    "target": target.mention,
                    "taxes" : taxes
                }))
            else:
                await comm.message_user(message, _("You don't have enough experience points", language))
        else:
            await comm.message_user(message, _(":x: Sending exp is disabled on this server", language))


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

        embed = discord.Embed(description=_("Statistics of {player} on #{channel}", language).format(**{
            "player" : target.name,
            "channel": message.channel.name
        }))
        embed.title = "DUCKSTATS"
        # embed.set_author(name=str(target), icon_url=target.avatar_url)
        embed.set_thumbnail(url=target.avatar_url if target.avatar_url else self.bot.user.avatar_url)
        embed.url = 'https://api-d.com/duckhunt/'
        embed.colour = discord.Colour.green()

        # embed.timestamp = datetime.datetime.now()

        if scores.getStat(message.channel, target, "canardsTues") > 0:
            ratio = round(scores.getStat(message.channel, target, "exp") / scores.getStat(message.channel, target, "canardsTues"), 4)
        else:
            ratio = _("No duck killed", language)
        embed.add_field(name=_("Ducks killed", language), value=str(scores.getStat(message.channel, target, "canardsTues")))
        embed.add_field(name=_("Shots missed", language), value=str(scores.getStat(message.channel, target, "tirsManques")))
        embed.add_field(name=_("Shots without ducks", language), value=str(scores.getStat(message.channel, target, "tirsSansCanards")))
        embed.add_field(name=_("Best killing time", language), value=str(scores.getStat(message.channel, target, "meilleurTemps", default=prefs.getPref(message.server, "time_before_ducks_leave"))))
        embed.add_field(name=_("Bullets in current charger", language), value=str(scores.getStat(message.channel, target, "balles", default=level["balles"])) + " / " + str(level["balles"]))
        embed.add_field(name=_("Exp points", language), value=str(scores.getStat(message.channel, target, "exp")))
        embed.add_field(name=_("Ratio (exp/ducks killed)", language), value=str(ratio))
        embed.add_field(name=_("Current level", language), value=str(level["niveau"]) + " (" + _(level["nom"], language) + ")")
        embed.add_field(name=_("Shots accuracy", language), value=str(level["precision"]))
        embed.add_field(name=_("Weapon fiability", language), value=str(level["fiabilitee"]))
        if scores.getStat(message.channel, target, "graisse", default=0) > int(time.time()):
            embed.add_field(name=_("Object : grease", language), value=str(self.objectTD(message.channel, target, language, "graisse")))
        if scores.getStat(message.channel, target, "detecteurInfra", default=0) > int(time.time()):
            embed.add_field(name=_("Object : infrared detector", language), value=str(self.objectTD(message.channel, target, language, "detecteurInfra")))
        if scores.getStat(message.channel, target, "silencieux", default=0) > int(time.time()):
            embed.add_field(name=_("Object : silencer", language), value=str(self.objectTD(message.channel, target, language, "silencieux")))
        if scores.getStat(message.channel, target, "trefle", default=0) > int(time.time()):
            embed.add_field(name=_("Object : clover {exp} exp", language).format(**{
                "exp": scores.getStat(message.channel, target, "trefle_exp", default=0)
            }), value=str(self.objectTD(message.channel, target, language, "trefle")))
        if scores.getStat(message.channel, target, "munExplo", default=0) > int(time.time()):
            embed.add_field(name=_("Object : explosive ammo", language), value=str(self.objectTD(message.channel, target, language, "munExplo")))
        elif scores.getStat(message.channel, target, "munAp_", default=0) > int(time.time()):
            embed.add_field(name=_("Object : AP ammo", language), value=str(self.objectTD(message.channel, target, language, "munAp_")))
        if scores.getStat(message.channel, target, "mouille", default=0) > int(time.time()):
            embed.add_field(name=_("Effect : wet", language), value=str(self.objectTD(message.channel, target, language, "mouille")))

        embed.set_footer(text='DuckHunt V2', icon_url='http://api-d.com/snaps/2016-11-19_10-38-54-q1smxz4xyq.jpg')
        try:
            await self.bot.say(embed=embed)
        except:
            commons.logger.exception("Error sending embed, with embed " + str(embed.to_dict()))
            await comm.message_user(message, _(":warning: Error sending embed, check if the bot have the permission embed_links and try again !", language))

    @commands.command(pass_context=True)
    @checks.is_not_banned()
    @checks.is_activated_here()
    async def top(self, ctx, number_of_scores: int = 10):
        language = prefs.getPref(ctx.message.server, "language")

        if number_of_scores != 10 or not prefs.getPref(ctx.message.server, "interactive_topscores_enabled"):  # TODO: check manage messages + embed_links permissions
            if number_of_scores > 200 or number_of_scores < 1:
                await comm.message_user(ctx.message, _(":x: The maximum number of scores that can be shown on a topscores table is 200.", language))
                return

            x = PrettyTable()

            x._set_field_names([_("Rank", language), _("Nickname", language), _("Exp points", language), _("Ducks killed", language)])

            i = 0
            for joueur in scores.topScores(ctx.message.channel):
                i += 1

                if (not "canardsTues" in joueur) or (joueur["canardsTues"] == 0) or ("canardTues" in joueur == False):
                    joueur["canardsTues"] = "AUCUN !"
                if joueur["exp"] is None:
                    joueur["exp"] = 0
                x.add_row([i, joueur["name"].replace("`", ""), joueur["exp"], joueur["canardsTues"]])

            await comm.message_user(ctx.message, _(":cocktail: Best scores for #{channel_name} : :cocktail:\n```{table}```", language).format(**{
                "channel_name": ctx.message.channel.name,
                "table"       : x.get_string(end=number_of_scores, sortby=_("Rank", language))
            }), )
        else:
            # \N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR} is >>|
            # \N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR} is |<<
            reaction = True
            changed = True

            next_emo = "\N{BLACK RIGHT-POINTING TRIANGLE}"
            prev_emo = "\N{BLACK LEFT-POINTING TRIANGLE}"
            first_page_emo = "\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}"

            current_page = 1

            message = await self.bot.send_message(ctx.message.channel, _("Generating topscores for your channel, please wait!", language))
            await self.bot.add_reaction(message, first_page_emo)
            await self.bot.add_reaction(message, prev_emo)
            await self.bot.add_reaction(message, next_emo)

            while reaction:
                if changed:


                    i = current_page * 10 - 10

                    scores_to_process = scores.topScores(ctx.message.channel)[i:i + 10]

                    if scores_to_process:
                        embed = discord.Embed(description="Page #{i}".format(i=current_page))
                        embed.title = _(":cocktail: Best scores for #{channel_name} :cocktail:", language).format(**{
                            "channel_name": ctx.message.channel.name,
                        })
                        embed.url = 'https://api-d.com/duckhunt/'
                        embed.colour = discord.Colour.green()
                        # embed.timestamp = datetime.datetime.now()
                        embed.url = 'https://api-d.com/duckhunt/'  # TODO: get the webinterface url and add it here inplace

                        players_list = ""
                        exp_list = ""
                        ducks_killed_list = ""


                        for joueur in scores_to_process:
                            i += 1
                            if (not "canardsTues" in joueur) or (joueur["canardsTues"] == 0) or ("canardTues" in joueur == False) or joueur["canardsTues"] is None:
                                joueur["canardsTues"] = _("None !", language)
                            if joueur["exp"] is None:
                                joueur["exp"] = 0

                            member = message.server.get_member(joueur["id_"])

                            if prefs.getPref(ctx.message.server, "mention_in_topscores"):

                                mention = member.mention if member else joueur["name"][:10]

                                # mention = mention if len(mention) < 20 else joueur["name"]
                                mention = mention if member and len(member.display_name) < 10 else joueur["name"][:10]
                            else:
                                mention = joueur["name"][:10]

                            players_list += "#{i} {name}".format(name=mention, i=i) + "\n\n"
                            exp_list += str(joueur["exp"]) + "\n\n"
                            ducks_killed_list += str(joueur["canardsTues"]) + "\n\n"

                        embed.add_field(name=_("Player", language), value=players_list, inline=True)
                        embed.add_field(name=_("Experience points", language), value=exp_list, inline=True)
                        embed.add_field(name=_("Number of ducks killed", language), value=ducks_killed_list, inline=True)

                        try:
                            await self.bot.edit_message(message, ":duck:", embed=embed)
                        except discord.errors.Forbidden:
                            await comm.message_user(message, _(":warning: Error sending embed, check if the bot have the permission embed_links and try again !", language))

                        changed = False
                    else:
                        current_page -= 1
                        await self.bot.edit_message(message, _("There is nothing more...", language))

                res = await self.bot.wait_for_reaction(emoji=[next_emo, prev_emo, first_page_emo], message=message, timeout=1200)

                if res:
                    reaction, user = res
                    emoji = reaction.emoji
                    if emoji == next_emo:
                        changed = True
                        current_page += 1
                        try:
                            await self.bot.remove_reaction(message, emoji, user)
                        except discord.errors.Forbidden:
                            await self.bot.send_message(message.channel, _("I don't have the `manage_messages` permissions, I can't remove reactions. Warn an admin for me, please ;)", language))
                    elif emoji == prev_emo:
                        if current_page > 1:
                            changed = True
                            current_page -= 1
                        try:
                            await self.bot.remove_reaction(message, emoji, user)
                        except discord.errors.Forbidden:
                            await self.bot.send_message(message.channel, _("I don't have the `manage_messages` permissions, I can't remove reactions. Warn an admin for me, please ;)", language))
                    elif emoji == first_page_emo:
                        if current_page > 1:
                            changed = True
                            current_page = 1
                        try:
                            await self.bot.remove_reaction(message, emoji, user)
                        except discord.errors.Forbidden:
                            await self.bot.send_message(message.channel, _("I don't have the `manage_messages` permissions, I can't remove reactions. Warn an admin for me, please ;)", language))
                else:
                    reaction = False
                    try:
                        await self.bot.delete_message(message)
                    except:
                        pass


    @commands.group(pass_context=True)
    @checks.is_not_banned()
    @checks.is_activated_here()
    async def shop(self, ctx):
        from cogs import shoot
        language = prefs.getPref(ctx.message.server, "language")

        await shoot.Shoot(self.bot).giveBackIfNeeded(ctx.message)
        if not ctx.invoked_subcommand:
            await comm.message_user(ctx.message, _(":x: Incorrect syntax : `!shop [list/item number] [argument if applicable]`", language))

    @shop.command(pass_context=True)
    async def list(self, ctx):
        language = prefs.getPref(ctx.message.server, "language")
        await comm.message_user(ctx.message, _("The list of items is available here : https://api-d.com/duckhunt/index.php/Shop", language))

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
            scores.setStat(message.channel, message.author, "munAP_", int(time.time() + DAY))
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
            scores.setStat(message.channel, message.author, "munExplo", int(time.time() + DAY))
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
        if scores.getStat(message.channel, message.author, "confisque", default=False):
            await comm.message_user(message, _(":money_with_wings: You take your weapon back for 40 exp points", language))
            scores.setStat(message.channel, message.author, "confisque", False)
            scores.addToStat(message.channel, message.author, "exp", -40)

        else:
            await comm.message_user(message, _(":champagne: You haven't killed anyone today, you have your weapon, what do you want to buy ? :p", language))

    @shop.command(pass_context=True, name="6")
    @checks.have_exp(8)
    async def item6(self, ctx):
        """Buy grease for your weapon (8 exp)
        !shop 6"""
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        if scores.getStat(message.channel, message.author, "graisse", default=0) < int(time.time()):
            await comm.message_user(message, _(":money_with_wings: You add grease in your weapon to reduce jamming risks by 50 percent for a day, for only 8 exp points.", language))
            scores.setStat(message.channel, message.author, "graisse", time.time() + DAY)
            scores.addToStat(message.channel, message.author, "exp", -8)

        else:
            await comm.message_user(message, _(":champagne: Your weapon is perfectly lubricated, no need for more grease", language))

    @shop.command(pass_context=True, name="7")
    @checks.have_exp(5)
    async def item7(self, ctx):
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        if not scores.getStat(message.channel, message.author, "sight", default=0):
            await comm.message_user(message, _(":money_with_wings: You add a sight to your weapon, for 5 exp points, your aiming was improved using this formulae : (100 - current accuracy) / 3. ", language))
            scores.setStat(message.channel, message.author, "sight", 6)
            scores.addToStat(message.channel, message.author, "exp", -5)
        else:
            await comm.message_user(message, _(":champagne: You already have a sight to your weapon. ", language))



    @shop.command(pass_context=True, name="8")
    @checks.have_exp(15)
    async def item8(self, ctx):
        """Buy an infrared detector (15 exp)
        !shop 8"""
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        if scores.getStat(message.channel, message.author, "detecteurInfra", default=0) < int(time.time()):
            await comm.message_user(message, _(":money_with_wings: You add an infrared detector to your weapon, that will prevent any waste of ammo for a day. Cost : 15 exp points.", language))
            scores.setStat(message.channel, message.author, "detecteurInfra", time.time() + DAY)
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
            scores.setStat(message.channel, message.author, "silencieux", time.time() + DAY)
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
        if scores.getStat(message.channel, message.author, "trefle", default=0) < int(time.time()):
            exp = random.randint(prefs.getPref(message.server, "clover_min_exp"), prefs.getPref(message.server, "clover_max_exp"))
            await comm.message_user(message, _(":money_with_wings: You buy a fresh 4-leaf clover, which will give you {exp} more exp point for the next day. You brought it for 13 exp!", language).format(**{
                "exp": exp
            }))
            scores.setStat(message.channel, message.author, "trefle", int(time.time()) + DAY)
            scores.setStat(message.channel, message.author, "trefle_exp", exp)
            scores.addToStat(message.channel, message.author, "exp", -13)

        else:
            await comm.message_user(message, _(":champagne: You're too lucky, but I don't have any clover left for you today :'(. Too much luck, maybe ??", language))

    @shop.command(pass_context=True, name="11")
    @checks.have_exp(5)
    async def item11(self, ctx):
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        if scores.getStat(message.channel, message.author, "sunglasses", default=0) > int(time.time()):
            await comm.message_user(message, _(":money_with_wings: You brought a pair of sunglasses for 5 exp ! You are now immune to sunlight for a day", language))
            scores.setStat(message.channel, message.author, "sunglasses", int(time.time()) + DAY)
            scores.setStat(message.channel, message.author, "dazzled", False)
            scores.addToStat(message.channel, message.author, "exp", -5)

        else:
            scores.addToStat(message.channel, message.author, "exp", -5)
            await comm.message_user(message, _(":money_with_wings: You brought brand new sunglasses, for nothing but the fact that you are mostly swag now. :cool:", language))


    @shop.command(pass_context=True, name="12")
    @checks.have_exp(7)
    async def item12(self, ctx):
        """Buy new clothes, dry ones :p (7 exp)
        !shop 12"""
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        if scores.getStat(message.channel, message.author, "mouille", default=0) > int(time.time()):
            await comm.message_user(message, _(":money_with_wings: You have some dry clothes on you now. You looks beautiful ! ", language))
            scores.setStat(message.channel, message.author, "mouille", 0)
            scores.addToStat(message.channel, message.author, "exp", -7)

        else:
            scores.addToStat(message.channel, message.author, "exp", -7)
            await comm.message_user(message, _(":money_with_wings: You brought brand new clothes, for nothing but the fact that you are mostly swag now. :cool:", language))

    @shop.command(pass_context=True, name="13")
    @checks.have_exp(6)
    async def item13(self, ctx):
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        scores.setStat(message.channel, message.author, "sabotee", "-")
        scores.setStat(message.channel, message.author, "sand", False)
        scores.addToStat(message.channel, message.author, "exp", -6)
        await comm.message_user(message, _(":champagne: You clean your weapon for 6 exp. If you had sand, or if your weapon was sabtaged, it's fixed now !", language))


    @shop.command(pass_context=True, name="14")
    @checks.have_exp(5)
    async def item14(self, ctx, target: discord.Member):
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        if scores.getStat(message.channel, target, "sunglasses", default=0) > int(time.time()):
            await comm.message_user(message, _(":x: No way ! {mention} have some sunglasses ! He is immune to this ! ", language).format(mention=target.mention))

        else:
            scores.addToStat(message.channel, message.author, "exp", -5)
            scores.setStat(message.channel, target, "dazzled", True)
            await comm.message_user(message, _(":money_with_wings: You dazzles {mention}! He loose 50% accuracy on his next shot !", language).format(mention=target.mention))



    @shop.command(pass_context=True, name="15")
    @checks.have_exp(7)
    async def item15(self, ctx, target: discord.Member):
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        scores.setStat(message.channel, target, "sand", True)
        scores.setStat(message.channel, message.author, "graisse", 0)
        scores.addToStat(message.channel, message.author, "exp", -6)
        await comm.message_user(message, _(":champagne: You throw sand on {mention} weapon!", language).format(mention=target.mention))

    @shop.command(pass_context=True, name="16")
    @checks.have_exp(10)
    async def item16(self, ctx, target: discord.Member):
        """ Drop a water bucket on someone (10 exp)
        !shop 16 [target]"""
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        await comm.message_user(message, _(":money_with_wings: You drop a full water bucket on {target}, forcing him to wait 1 hour for his/her clothes to dry before he/she can return hunting", language).format(**{
            "target": target.name
        }))
        scores.setStat(message.channel, target, "mouille", int(time.time()) + HOUR)
        scores.addToStat(message.channel, message.author, "exp", -10)

    @shop.command(pass_context=True, name="17")
    @checks.have_exp(14)
    async def item17(self, ctx, target: discord.Member):
        """Sabotage a weapon
        !shop 17 [target]"""
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
        try:
            self.bot.delete_message(ctx.message)
        except discord.Forbidden:
            comm.logwithinfos_ctx(ctx, "Error deleting command : forbidden")

    @shop.command(pass_context=True, name="18")
    @checks.have_exp(10)
    async def item18(self, ctx):
        """Buy a life insurance (10 exp)
        !shop 18"""
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
        """Buy a decoy (8 exp)
        !shop 20"""
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        await comm.message_user(message, _(":money_with_wings: A duck will appear in the next 10 minutes on the channel, thanks to the decoy of {mention}. He brought it for 8 exp !", language).format(**{
            "mention": message.author.mention
        }))
        scores.addToStat(message.channel, message.author, "exp", -8)
        dans = random.randint(0, 60 * 10)
        await asyncio.sleep(dans)
        await ducks.spawn_duck({
            "time"   : int(time.time()),
            "channel": message.channel
        })

    @shop.command(pass_context=True, name="21")
    async def item21(self, ctx):
        raise NotImplementedError

    @shop.command(pass_context=True, name="22")
    @checks.have_exp(5)
    async def item22(self, ctx):

        """Buy a ducktector (5 exp)
        !shop 22"""
        servers = prefs.JSONloadFromDisk("channels.json", default="{}")
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        await comm.message_user(message, _(":money_with_wings: You will be warned when the next duck on #{channel_name} spawns", language).format(**{
            "channel_name": message.channel.name
        }), forcePv=True)
        if not "detecteur" in servers[message.server.id]:
            servers[message.server.id]["detecteur"] = {}
        if message.channel.id in servers[message.server.id]["detecteur"]:
            servers[message.server.id]["detecteur"][message.channel.id].append(message.author.id)
        else:
            servers[message.server.id]["detecteur"][message.channel.id] = [message.author.id]
        prefs.JSONsaveToDisk(servers, "channels.json")
        scores.addToStat(message.channel, message.author, "exp", -5)

    @shop.command(pass_context=True, name="23")
    @checks.have_exp(40)
    async def item23(self, ctx):
        """Buy a mechanical duck (40 exp)
        !shop 23"""
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        await comm.message_user(message, _(":money_with_wings: You prepare a mechanical duck on the channel for 50 exp. That's bad, but so funny !", language), forcePv=True)
        scores.addToStat(message.channel, message.author, "exp", -50)
        try:
            self.bot.delete_message(ctx.message)
        except discord.Forbidden:
            comm.logwithinfos_ctx(ctx, "Error deleting command : forbidden")
        await asyncio.sleep(75)
        try:
            if prefs.getPref(message.server, "emoji_ducks"):
                if prefs.getPref(message.server, "randomize_mechanical_ducks") == 0:
                    await self.bot.send_message(message.channel, _(":duck: < *BZAACK*", language))
                else:
                    await self.bot.send_message(message.channel, _(":duck: < " + _(random.choice(commons.canards_cri), language)))
            else:

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
