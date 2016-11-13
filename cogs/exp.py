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
                await comm.message_user(message,
                                        _("You sent {amount} exp to {target} (and paid {taxes} exp of taxes for this transfer) !", language).format(
                                                **{
                                                    "amount": amount - taxes,
                                                    "target": target.mention,
                                                    "taxes" : taxes
                                                }))
                comm.logwithinfos_message(message, "[sendexp] Exp envoyé à {target} : {amount} exp et {taxes}".format(
                        **{
                            "amount": amount - taxes,
                            "target": target.mention,
                            "taxes" : taxes
                        }))
            else:
                comm.logwithinfos_message(message, "[sendexp] manque d'experience")
                await comm.message_user(message, _("Vous n'avez pas assez d'experience", language))


def setup(bot):
    bot.add_cog(Exp(bot))
