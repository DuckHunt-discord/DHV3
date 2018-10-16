import datetime
import random

import discord
import time
from discord.ext import commands
from cogs.helpers import checks
from cogs import spawning


class Experience:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['giveexp', 'give_xp', 'givexp'])
    @checks.is_server_admin()
    @checks.is_channel_enabled()
    async def give_exp(self, ctx, target:discord.Member, amount:int):
        _ = self.bot._
        language = await self.bot.db.get_pref(ctx.guild, "language")

        try:
            await self.bot.db.add_to_stat(ctx.message.channel, target, "exp", amount)
        except OverflowError:
            await self.bot.send_message(ctx=ctx, message=_("Congratulations, you sent / gave more experience than the maximum "
                                                           "number I'm able to store.", await self.bot.db.get_pref(ctx.guild, "language")))
            return

        await self.bot.send_message(ctx=ctx, message=_(":ok:, he/she now has {newexp} exp points!", language).format(**{"newexp": await self.bot.db.get_stat(ctx.message.channel, target, "exp")}))

    @commands.command(aliases=["thank", "thanksyou"])
    @checks.is_channel_enabled()
    @checks.had_giveback()
    async def thanks(self, ctx, user:discord.Member = None):
        if not user:
            user = ctx.guild.get_member(138751484517941259)  # Eyes
            if not user:
                user = random.choice([m for m in ctx.guild.members if not m.bot])

        cmd = self.bot.get_command("send_exp")
        await ctx.invoke(cmd, target=user, amount=15)

    @commands.command(aliases=['sendexp', 'send_xp', 'sendxp'])
    @checks.is_channel_enabled()
    @checks.had_giveback()
    async def send_exp(self, ctx, target: discord.Member, amount: int):
        _ = self.bot._
        language = await self.bot.db.get_pref(ctx.guild, "language")

        message = ctx.message
        if await self.bot.db.get_pref(message.guild, "user_can_give_exp"):
            if await self.bot.db.get_stat(message.channel, message.author, "confisque"):  # No weapon
                await self.bot.send_message(ctx=ctx, message=_(":x: To prevent abuse, you can't send exp when you don't have a weapon.", language))
                return

            if amount <= 0:
                await self.bot.send_message(ctx=ctx, message=_(":x: The exp amount needs to be positive.", language))
                return

            if target == ctx.message.author:
                await self.bot.send_message(ctx=ctx, message=_(":x: Wait... What? Are you trying to send experience to YOURSELF? That doesn't make sense.", language))
                return

            if await self.bot.db.get_stat(message.channel, message.author, "exp") >= amount:
                await self.bot.db.add_to_stat(message.channel, message.author, "exp", -amount)
                tax = await self.bot.db.get_pref(message.guild, "tax_on_user_give")

                if tax > 0:
                    taxes = amount * tax / 100
                else:
                    taxes = 0
                # try:

                await self.bot.db.add_to_stat(message.channel, target, "exp", amount - taxes)

                # except OverflowError:
                #    await comm.message_user(ctx.message, _("Congratulations, you sent more experience than the maximum number I'm able to store.", language))
                #    return

                await self.bot.send_message(ctx=ctx, message=_("You sent {amount} exp to {target} (and paid {taxes} exp of taxes)!", language).format(
                    **{"amount": amount - taxes, "target": target.mention, "taxes": taxes}))
            else:
                await self.bot.send_message(ctx=ctx, message=_("You don't have enough experience points", language))
        else:
            await self.bot.send_message(ctx=ctx, message=_(":x: Sending exp is disabled on this server", language))

    async def objectTD(self, gs, object):
        date_expiration = datetime.datetime.fromtimestamp(gs(object))
        td = date_expiration - datetime.datetime.now()
        _ = gs.bot._
        language = await self.bot.db.get_pref(gs.channel.guild, "language")

        return _("{date} (in {dans_jours}{dans_heures} and {dans_minutes})", language).format(
            **{"date": date_expiration.strftime(_('%m/%d at %H:%M:%S', language)), "dans_jours": _("{dans} days ", language).format(**{"dans": td.days}) if td.days else "",
                "dans_heure": _("{dans} hours", language).format(**{"dans": td.seconds // 3600}), "dans_minutes": _("{dans} minutes", language).format(**{"dans": (td.seconds // 60) % 60})})


def setup(bot):
    bot.add_cog(Experience(bot))
