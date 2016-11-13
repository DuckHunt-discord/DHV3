# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5

"""

"""

import discord
from discord.ext import commands

from cogs.utils import checks, comm, prefs, scores
from cogs.utils.commons import _


class Exp:
    """Commends to use, spend and give exp."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @checks.is_not_banned()
    @checks.is_activated_here()
    async def sendexp(self, ctx, target: discord.Member, amount: int):
        message = ctx.message
        language = prefs.getPref(message.server, "language")
        if prefs.getPref(message.server, "user_can_give_exp"):

            if amount <= 0:
                await comm.message_user(message, _(":x: Essaye de préciser un montant valide, c'est a dire positif et entier", language))
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
                comm.logwithinfos_message(message, "[sendexp] Exp envoyé à {target} : {amount} exp et {taxes}".format(**{
                    "amount": amount - taxes,
                    "target": target.mention,
                    "taxes" : taxes
                }))
            else:
                comm.logwithinfos_message(message, "[sendexp] manque d'experience")
                await comm.message_user(message, _("Vous n'avez pas assez d'experience", language))

    @commands.command(pass_context=True)
    @checks.is_not_banned()
    @checks.is_activated_here()
    async def duckstats(self, ctx, target: discord.Member):
        raise NotImplementedError

    @commands.command(pass_context=True)
    @checks.is_not_banned()
    @checks.is_activated_here()
    async def top(self, ctx, number_of_scores: int):
        raise NotImplementedError

    @commands.group(pass_context=True)
    @checks.is_not_banned()
    @checks.is_activated_here()
    async def shop(self, ctx):
        raise NotImplementedError

    @shop.command(pass_context=True, name="1")
    async def item1(self, ctx):
        raise NotImplementedError

    @shop.command(pass_context=True, name="2")
    async def item2(self, ctx):
        raise NotImplementedError

    @shop.command(pass_context=True, name="3")
    async def item3(self, ctx):
        raise NotImplementedError

    @shop.command(pass_context=True, name="4")
    async def item4(self, ctx):
        raise NotImplementedError

    @shop.command(pass_context=True, name="5")
    async def item5(self, ctx):
        raise NotImplementedError

    @shop.command(pass_context=True, name="6")
    async def item6(self, ctx):
        raise NotImplementedError

    @shop.command(pass_context=True, name="7")
    async def item7(self, ctx):
        raise NotImplementedError

    @shop.command(pass_context=True, name="8")
    async def item8(self, ctx):
        raise NotImplementedError

    @shop.command(pass_context=True, name="9")
    async def item9(self, ctx):
        raise NotImplementedError

    @shop.command(pass_context=True, name="10")
    async def item10(self, ctx):
        raise NotImplementedError

    @shop.command(pass_context=True, name="11")
    async def item11(self, ctx):
        raise NotImplementedError

    @shop.command(pass_context=True, name="12")
    async def item12(self, ctx):
        raise NotImplementedError

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
    async def item16(self, ctx):
        raise NotImplementedError

    @shop.command(pass_context=True, name="17")
    async def item17(self, ctx):
        raise NotImplementedError

    @shop.command(pass_context=True, name="18")
    async def item18(self, ctx):
        raise NotImplementedError

    @shop.command(pass_context=True, name="19")
    async def item19(self, ctx):
        raise NotImplementedError

    @shop.command(pass_context=True, name="20")
    async def item20(self, ctx):
        raise NotImplementedError

    @shop.command(pass_context=True, name="21")
    async def item21(self, ctx):
        raise NotImplementedError

    @shop.command(pass_context=True, name="22")
    async def item22(self, ctx):
        raise NotImplementedError

    @shop.command(pass_context=True, name="23")
    async def item23(self, ctx):
        raise NotImplementedError

    @shop.command(pass_context=True, name="24")
    async def item24(self, ctx):
        raise NotImplementedError


def setup(bot):
    bot.add_cog(Exp(bot))
