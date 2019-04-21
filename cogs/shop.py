import datetime
import random

import asyncio
import discord
import time
from discord.ext import commands
from discord.ext.commands import BucketType

from cogs.helpers import checks
from cogs.helpers import ducks

from cogs import spawning

HOUR = 3600
DAY = 86400


class Get_Stats:
    def __init__(self, bot, channel, target):
        self.channel = channel
        self.target = target
        self.bot = bot

    async def __call__(self, stat):
        return await self.bot.db.get_stat(self.channel, self.target, stat)


class Experience:
    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=["buy", "shopping"])
    @checks.is_channel_enabled()
    @checks.had_giveback()
    @commands.cooldown(10, 20, BucketType.user)
    async def shop(self, ctx):
        _ = self.bot._;
        language = await self.bot.db.get_pref(ctx.guild, "language")

        if not ctx.invoked_subcommand:
            await ctx.bot.send_message(ctx=ctx, message=_(":x: Incorrect syntax. Use the command this way: `!shop [list/item number] [argument if applicable]`", language))

    async def __after_invoke(self, ctx):
        # print('{0.command} is done...'.format(ctx))

        _ = self.bot._;
        language = await self.bot.db.get_pref(ctx.guild, "language")

        if ctx.command.parent == self.shop:
            await self.bot.send_message(ctx=ctx,
                                        message=_("Right now you have a total of {exp} exp points.", language).format(exp=await self.bot.db.get_stat(ctx.message.channel, ctx.message.author, "exp")))

    @shop.command()
    async def list(self, ctx):
        _ = self.bot._;
        language = await self.bot.db.get_pref(ctx.guild, "language")

        await self.bot.send_message(ctx=ctx, message=_("Here is the list of all the shops items : https://duckhunt.me/shop-items/ . Thanks ", language))

    @shop.command(name="1", aliases=["bullet", "bullets"])
    @checks.have_exp(7)
    async def item1(self, ctx):
        """Add a bullet to your weapon (7 exp)
        !shop 1"""
        message = ctx.message
        _ = self.bot._;
        language = await self.bot.db.get_pref(ctx.guild, "language")

        if await self.bot.db.get_stat(message.channel, message.author, "balles") < (await self.bot.db.get_level(channel=message.channel, player=message.author))["balles"]:

            await self.bot.db.add_to_stat(message.channel, message.author, "balles", 1)
            await self.bot.db.add_to_stat(message.channel, message.author, "exp", -7)

            await self.bot.send_message(ctx=ctx, message=_(":money_with_wings: You added a bullet to your weapon for 7 exp points.", language))

        else:
            await self.bot.send_message(ctx=ctx, message=_(":champagne: Your magazine is full!", language))

    @shop.command(name="2", aliases=["charger", "chargers", "magazine", "magazines"])
    @checks.have_exp(13)
    async def item2(self, ctx):
        """Add a charger to your weapon (13 exp)
        !shop 2"""
        message = ctx.message
        _ = self.bot._
        language = await self.bot.db.get_pref(ctx.guild, "language")

        if await self.bot.db.get_stat(message.channel, message.author, "chargeurs") < (await self.bot.db.get_level(channel=message.channel, player=message.author))["chargeurs"]:

            await self.bot.db.add_to_stat(message.channel, message.author, "chargeurs", 1)
            await self.bot.db.add_to_stat(message.channel, message.author, "exp", -13)

            await self.bot.send_message(ctx=ctx, message=_(":money_with_wings: You added a magazine to your weapon for 13 exp points.", language))

        else:
            await self.bot.send_message(ctx=ctx, message=_(":champagne: You have enough magazines!", language))

    @shop.command(name="3", aliases=["AP", "ap_ammo", "apammo"])
    @checks.have_exp(15)
    async def item3(self, ctx):
        """Buy AP ammo (15 exp)
        !shop 3"""
        message = ctx.message
        _ = self.bot._;
        language = await self.bot.db.get_pref(ctx.guild, "language")

        if await self.bot.db.get_stat(message.channel, message.author, "ap_ammo") < time.time():
            await self.bot.db.set_stat(message.channel, message.author, "ap_ammo", int(time.time() + DAY))
            await self.bot.db.add_to_stat(message.channel, message.author, "exp", -15)
            await self.bot.send_message(ctx=ctx, message=_(":money_with_wings: You purchased AP ammo for your weapon.", language))
            await self.bot.hint(ctx=ctx, message=_("For the next 24 hours, you will deal double damage to ducks. This does **not** stack with explosive ammo", language))

        else:
            await self.bot.send_message(ctx=ctx, message=_(":champagne: You have enough AP ammo for now!", language))

    @shop.command(name="4", aliases=["explosive", "explosive_ammo", "explosiveammo"])
    @checks.have_exp(25)
    async def item4(self, ctx):
        """Buy Explosive ammo (25 exp)
        !shop 4"""
        message = ctx.message
        _ = self.bot._;
        language = await self.bot.db.get_pref(ctx.guild, "language")

        if await self.bot.db.get_stat(message.channel, message.author, "explosive_ammo") < time.time():
            await self.bot.db.set_stat(message.channel, message.author, "explosive_ammo", int(time.time() + DAY))
            await self.bot.db.add_to_stat(message.channel, message.author, "exp", -25)
            await self.bot.send_message(ctx=ctx, message=_(":money_with_wings: You purchased explosive ammo for your weapon.", language))
            await self.bot.hint(ctx=ctx, message=_("For the next 24 hours, you will deal triple damage to ducks. This does **not** stack with AP ammo and trumps it if you have any.", language))

        else:
            await self.bot.send_message(ctx=ctx, message=_(":champagne: You have enough explosive ammo for now!", language))

    @shop.command(name="5", aliases=["giveback", "weapon", "give_back", "weapon_giveback", "confiscated_weapon", "gun"])
    @checks.have_exp(40)
    async def item5(self, ctx):
        """Get back your weapon (40 exp)
        !shop 5"""
        message = ctx.message
        _ = self.bot._;
        language = await self.bot.db.get_pref(ctx.guild, "language")

        if await self.bot.db.get_stat(message.channel, message.author, "confisque"):
            await self.bot.db.set_stat(message.channel, message.author, "confisque", False)
            await self.bot.db.add_to_stat(message.channel, message.author, "exp", -40)
            await self.bot.send_message(ctx=ctx, message=_(":money_with_wings: You got your weapon back.", language))
            await self.bot.hint(ctx=ctx, message=_("You can get your weapon back for free if you wait until the daily weapon & magazine giveback. "
                                                   "Type `dh!freetime` to find out when the next giveback is", language))

        else:
            await self.bot.send_message(ctx=ctx, message=_(":champagne: You already have your weapon, what are you trying to buy? :p", language))

    @shop.command(name="6", aliases=["grease", "lubricate", "lubricator"])
    @checks.have_exp(8)
    async def item6(self, ctx):
        """Buy grease for your weapon (8 exp)
        !shop 6"""
        message = ctx.message
        _ = self.bot._;
        language = await self.bot.db.get_pref(ctx.guild, "language")

        if await self.bot.db.get_stat(message.channel, message.author, "graisse") < time.time():
            await self.bot.db.set_stat(message.channel, message.author, "graisse", int(time.time() + DAY))
            await self.bot.db.add_to_stat(message.channel, message.author, "exp", -8)
            await self.bot.send_message(ctx=ctx, message=_(":money_with_wings: You added grease in your weapon.", language))
            await self.bot.hint(ctx=ctx, message=_("This reduces jamming risks by 50 percent for a day, for only 8 exp points. It's really useful for new players. Use `dh!duckstats` to check your "
                                                   "level and accuracy", language))

        else:
            await self.bot.send_message(ctx=ctx, message=_(":champagne: Your weapon is perfectly lubricated, you don't need any more grease.", language))

    @shop.command(name="7", aliases=["sight", "scope"])
    @checks.have_exp(5)
    async def item7(self, ctx):
        """
        Buy a sight for your weapon (5 exp)
        !shop 7
        """
        message = ctx.message
        _ = self.bot._;
        language = await self.bot.db.get_pref(ctx.guild, "language")

        if not await self.bot.db.get_stat(message.channel, message.author, "sight"):
            await self.bot.db.set_stat(message.channel, message.author, "sight", 6)
            await self.bot.db.add_to_stat(message.channel, message.author, "exp", -5)
            await self.bot.send_message(ctx=ctx, message=_(":money_with_wings: You added a sight to your weapon.", language))
            await self.bot.hint(ctx=ctx, message=_("Your aiming was improved using this formula: (100 - current accuracy) / 3.", language))

        else:
            await self.bot.send_message(ctx=ctx, message=_(":champagne: You already have a sight on your weapon.", language))

    @shop.command(name="8", aliases=["infrared", "infrared_detector", "infrareddetector", "detector"])
    @checks.have_exp(5)
    async def item8(self, ctx):
        """Buy an infrared detector (15 exp)
        !shop 8"""
        message = ctx.message
        _ = self.bot._;
        language = await self.bot.db.get_pref(ctx.guild, "language")

        if await self.bot.db.get_stat(message.channel, message.author, "detecteurInfra") < time.time() or await self.bot.db.get_stat(message.channel, message.author,
                                                                                                                                     "detecteur_infra_shots_left") <= 0:
            await self.bot.db.set_stat(message.channel, message.author, "detecteurInfra", int(time.time() + DAY))
            await self.bot.db.set_stat(message.channel, message.author, "detecteur_infra_shots_left", 6)
            await self.bot.db.add_to_stat(message.channel, message.author, "exp", -15)
            await self.bot.send_message(ctx=ctx,
                                        message=_(":money_with_wings: You added an infrared detector to your weapon, it will prevent any waste of ammo for a day. Cost: 15 exp points.", language))
        else:
            await self.bot.send_message(ctx=ctx, message=_(":champagne: You already have an infrared detector on your weapon.", language))

    @shop.command(name="9", aliases=["silencer"])
    @checks.have_exp(5)
    async def item9(self, ctx):
        """Buy a silencer for your weapon (5 exp)
        !shop 9"""
        message = ctx.message
        _ = self.bot._;
        language = await self.bot.db.get_pref(ctx.guild, "language")

        if await self.bot.db.get_stat(message.channel, message.author, "silencieux") < time.time():
            await self.bot.db.set_stat(message.channel, message.author, "silencieux", int(time.time() + DAY))
            await self.bot.db.add_to_stat(message.channel, message.author, "exp", -5)
            await self.bot.send_message(ctx=ctx, message=_(":money_with_wings: You added a silencer to your weapon.", language))
            await self.bot.hint(ctx=ctx, message=_("The silencer works best if every hunter uses one, or if you're alone. "
                                                   "With it, no ducks will fly away before you can kill them. What a good deal, they only cost 5 exp!", language))

        else:
            await self.bot.send_message(ctx=ctx, message=_(":champagne: You already have a silencer on your weapon", language))

    @shop.command(name="10", aliases=["4leaf", "four_leaf_clover", "four_leaf", "4_leaf", "4_leaf_clover", "fourleaf", "clover"])
    @checks.have_exp(13)
    async def item10(self, ctx):
        """Buy a 4leaf clover (13 exp)
        !shop 10"""
        message = ctx.message
        _ = self.bot._;
        language = await self.bot.db.get_pref(ctx.guild, "language")

        if await self.bot.db.get_stat(message.channel, message.author, "trefle") < time.time():
            min_c = await self.bot.db.get_pref(ctx.guild, "clover_min_exp")
            max_c = await self.bot.db.get_pref(ctx.guild, "clover_max_exp")

            if ctx.bot.current_event['id'] == 6:
                max_c += ctx.bot.current_event['ammount_to_add_to_max_exp']

            exp = random.randint(min(min_c, max_c), max(min_c, max_c))

            await self.bot.db.set_stat(message.channel, message.author, "trefle", int(time.time() + DAY))
            await self.bot.db.set_stat(message.channel, message.author, "trefle_exp", exp)
            await self.bot.db.add_to_stat(message.channel, message.author, "exp", -13)

            await self.bot.send_message(ctx=ctx, message=_(":money_with_wings: You bought a fresh 4-leaf clover, "
                                                           "which will give you {exp} more exp points for each killed duck for the next day.", language).format(**{"exp": exp}))

        else:
            await self.bot.send_message(ctx=ctx, message=_(":champagne: You already have 4-leaf clover on your weapon", language))

    @shop.command(name="11", aliases=["sunglasses"])
    @checks.have_exp(5)
    async def item11(self, ctx):
        """Buy sunglasses (5 exp)
        !shop 11"""
        message = ctx.message
        _ = self.bot._;
        language = await self.bot.db.get_pref(ctx.guild, "language")

        if await self.bot.db.get_stat(message.channel, message.author, "sunglasses") < time.time():
            await self.bot.db.set_stat(message.channel, message.author, "sunglasses", int(time.time() + DAY))
            await self.bot.db.set_stat(message.channel, message.author, "dazzled", False)

            await self.bot.db.add_to_stat(message.channel, message.author, "exp", -5)
            await self.bot.send_message(ctx=ctx, message=_(":money_with_wings: You bought a pair of sunglasses for 5 exp! You now won't be dazzled for a day.", language))

        else:
            await self.bot.db.add_to_stat(message.channel, message.author, "exp", -5)
            await self.bot.send_message(ctx=ctx, message=_(":money_with_wings: You bought brand new sunglasses, the only point of it being that you're much swagger now. :cool:", language))
            await self.bot.hint(ctx=ctx, message=_("Don't buy sunglasses if you still have some! This doesn't extend the time you won't be dazzled, but still costs you some exp", language))

    @shop.command(name="12", aliases=["clothes", "dry", "dry_clothes"])
    @checks.have_exp(7)
    async def item12(self, ctx):
        """Buy dry clothes (7 exp)
        !shop 12"""
        message = ctx.message
        _ = self.bot._;
        language = await self.bot.db.get_pref(ctx.guild, "language")

        if await self.bot.db.get_stat(message.channel, message.author, "mouille") > time.time():
            await self.bot.db.set_stat(message.channel, message.author, "mouille", 0)
            await self.bot.db.add_to_stat(message.channel, message.author, "exp", -7)
            await self.bot.send_message(ctx=ctx, message=_(":money_with_wings: You're wearing new dry clothes. You look fantastic!", language))

        else:
            await self.bot.db.add_to_stat(message.channel, message.author, "exp", -7)
            await self.bot.send_message(ctx=ctx, message=_(":money_with_wings: You bought brand new clothes, the only point of it being that you're much swagger now. :cool:", language))
            await self.bot.hint(ctx=ctx, message=_("Don't buy dry clothes if you aren't wet! They won't do anything, but will still cost you exp", language))

    @shop.command(name="13", aliases=["clean", "cleanup", "weapon_cleanup"])
    @checks.have_exp(6)
    async def item13(self, ctx):
        """Clean your weapon (6 exp)
        !shop 13"""
        message = ctx.message
        _ = self.bot._;
        language = await self.bot.db.get_pref(ctx.guild, "language")

        await self.bot.db.set_stat(message.channel, message.author, "sabotee", "-")
        await self.bot.db.set_stat(message.channel, message.author, "sand", False)
        await self.bot.db.add_to_stat(message.channel, message.author, "exp", -6)
        await self.bot.send_message(ctx=ctx, message=_(":money_with_wings: You cleaned your weapon for 6 exp. If you had sand in it, or if your weapon was sabotaged, it's fixed now!", language))
        await self.bot.hint(ctx=ctx, message=_("Next time someone sabotages you, just shot. It won't do much damage except for hurting your reputation", language))

    @shop.command(name="14", aliases=["dazzle", "mirror"])
    @checks.have_exp(5)
    async def item14(self, ctx, target: discord.Member):
        """Dazzle someone (5 exp)
        !shop 14 [target]"""
        message = ctx.message
        _ = self.bot._;
        language = await self.bot.db.get_pref(ctx.guild, "language")

        if await self.bot.db.get_stat(message.channel, target, "sunglasses") > time.time():
            await self.bot.db.add_to_stat(message.channel, message.author, "exp", -5)
            await self.bot.send_message(ctx=ctx, message=_(":x: No way! {mention} has sunglasses! They're immunised against this!", language).format(mention=target.mention))
            await self.bot.hint(ctx=ctx, message=_("That bad move still took 5 exp from your account, due to you having to buy a mirror", language))

        else:
            await self.bot.db.add_to_stat(message.channel, message.author, "exp", -5)
            await self.bot.db.set_stat(message.channel, target, "dazzled", True)
            await self.bot.send_message(ctx=ctx, message=_(":money_with_wings: You dazzled {mention}! Their next shot will lose 50% accuracy!", language).format(mention=target.mention))
            await self.bot.hint(ctx=ctx, message=_("The mention is here on purpose. You wouldn't do this behind their back, would you?", language))

    @shop.command(name="15", aliases=["sand"])
    @checks.have_exp(7)
    async def item15(self, ctx, target: discord.Member):
        """Throw sand in someone weapon (7 exp)
        !shop 15"""
        message = ctx.message
        _ = self.bot._;
        language = await self.bot.db.get_pref(ctx.guild, "language")

        await self.bot.db.set_stat(message.channel, target, "graisse", 0)
        await self.bot.db.set_stat(message.channel, target, "sand", True)
        await self.bot.db.add_to_stat(message.channel, message.author, "exp", -6)
        await self.bot.send_message(ctx=ctx, message=_(":champagne: You threw sand in {mention}'s weapon!", language).format(mention=target.mention))
        await self.bot.hint(ctx=ctx, message=_("The mention is here on purpose. You wouldn't do this behind their back, would you", language))

    @shop.command(name="16", aliases=["water", "water_bucket", "bucket", "bukkit", "spigot"])  # wink, wink
    @checks.have_exp(10)
    async def item16(self, ctx, target: discord.Member):
        """ Drop a water bucket on someone (10 exp)
        !shop 16 [target]"""
        message = ctx.message
        _ = self.bot._;
        language = await self.bot.db.get_pref(ctx.guild, "language")

        await self.bot.db.set_stat(message.channel, target, "mouille", int(time.time()) + HOUR)
        await self.bot.db.add_to_stat(message.channel, message.author, "exp", -10)
        await self.bot.send_message(ctx=ctx, message=_(":money_with_wings: You dropped a bucket full of water on {target}, "
                                                       "forcing them to wait 1 hour for their clothes to dry before they can return hunting.", language).format(**{"target": target.name}))

    @shop.command(name="16special", aliases=["specialwater", "specialwater_bucket", "specialbucket", "specialbukkit", "specialspigot"])  # wink, wink
    @checks.have_exp(30)
    async def item16special(self, ctx, target: discord.Member):
        """ Drop a SUPER water bucket on someone (10 exp)
        !shop 16special [target]"""

        message = ctx.message
        _ = self.bot._;
        language = await self.bot.db.get_pref(ctx.guild, "language")

        if not ctx.author.id == 138751484517941259:
            await self.bot.send_message(ctx=ctx, message="🖕")
            return

        await self.bot.db.set_stat(message.channel, target, "mouille", int(time.time()) + 2 * HOUR)
        await self.bot.db.add_to_stat(message.channel, message.author, "exp", -30)
        await self.bot.send_message(ctx=ctx, message=_(":money_with_wings: You dropped a **SPECIAL** bucket full of water on {target}, "
                                                       "forcing them to wait 2 hours (!) for their clothes to dry before they can return hunting.", language).format(**{"target": target.name}))


    @shop.command(name="17", aliases=["sabotage", "prank"])
    @checks.have_exp(14)
    async def item17(self, ctx, target: discord.Member):
        """ Sabotage another hunter weapon (14 exp)
        !shop 17 [target]"""
        message = ctx.message
        _ = self.bot._;
        language = await self.bot.db.get_pref(ctx.guild, "language")

        if target == ctx.message.author:
            await self.bot.send_message(ctx=ctx, force_pm=True, message=_("You wouldn't sabotage yourself, would you ?", language))
            return

        if await self.bot.db.get_stat(message.channel, target, "sabotee") == "-":
            await self.bot.db.add_to_stat(message.channel, message.author, "exp", -14)
            await self.bot.db.set_stat(message.channel, target, "sabotee", message.author.name)
            await self.bot.send_message(ctx=ctx, force_pm=True, message=_(":ok: {target} weapon is now sabotaged... but they don't know it (14 exp)!", language).format(**{"target": target.mention}))

            if target in ctx.message.mentions:
                await self.bot.hint(ctx=ctx, message=_("Don't use a mention for this. You can give me user ids or the full username in \"quotes\"", language))


        else:
            await self.bot.send_message(ctx=ctx, force_pm=True, message=_(":ok: {target}'s weapon is already sabotaged!", language).format(**{"target": target.mention}))

        try:
            await ctx.message.delete()
        except discord.Forbidden:
            await self.bot.hint(ctx=ctx, message=_("If you ask a server admin to give me the `manage_message` permission, I will be able to delete that kind of shop commands ;)", language))
        except discord.NotFound:
            pass

    @shop.command(name="18", aliases=["life_insurance", "insurance"])
    @checks.have_exp(10)
    async def item18(self, ctx):
        """Buy a life insurance (10 exp)
        !shop 18"""

        message = ctx.message
        _ = self.bot._;
        language = await self.bot.db.get_pref(ctx.guild, "language")

        if await self.bot.db.get_stat(message.channel, message.author, "life_insurance") < time.time():
            await self.bot.db.set_stat(message.channel, message.author, "life_insurance", int(time.time() + DAY * 7))
            await self.bot.db.add_to_stat(message.channel, message.author, "exp", -10)
            await self.bot.send_message(ctx=ctx, message=_(":money_with_wings: You bought a life insurance for a week for 10 exp.", language))
            await self.bot.hint(ctx=ctx, message=_("If you get killed, you'll earn half the level of the killer in exp.", language))

        else:
            await self.bot.send_message(ctx=ctx, message=_(":champagne: You're already insured.", language))

    @shop.command(name="19", aliases=["NOT"])
    @checks.have_exp(8)
    async def shop19(self, ctx):
        raise NotImplementedError

    @shop.command(name="20", aliases=["decoy"])
    @checks.have_exp(8)
    async def item20(self, ctx):
        """Buy a decoy (8 exp)
        !shop 20"""
        _ = self.bot._;
        language = await self.bot.db.get_pref(ctx.guild, "language")
        message = ctx.message
        channel = message.channel

        currently_sleeping = False

        if await self.bot.db.get_pref(ctx.guild, "disable_decoys_when_ducks_are_sleeping"):
            sdstart = await self.bot.db.get_pref(ctx.guild, "sleeping_ducks_start")
            sdstop = await self.bot.db.get_pref(ctx.guild, "sleeping_ducks_stop")

            now = time.time()
            thishour = int((now % DAY) / HOUR)

            if sdstart != sdstop:  # Dans ce cas, les canards dorment peut-etre!
                if sdstart < sdstop:  # 00:00 |-----==========---------| 23:59
                    if sdstart <= thishour < sdstop:
                        currently_sleeping = True
                else:  # 00:00 |====--------------======| 23:59
                    if thishour >= sdstart or thishour < sdstop:
                        currently_sleeping = True

        await self.bot.db.add_to_stat(message.channel, message.author, "exp", -8)

        if currently_sleeping:
            await self.bot.hint(ctx=ctx, message=_(":money_with_wings: Ducks are resting right now, so your decoy probably didn't work...", language))
            return

        await self.bot.send_message(ctx=ctx,
                                    message=_(":money_with_wings: A duck will appear in the next 10 minutes on the channel, thanks to {mention}'s decoy. They bought it for 8 exp!", language).format(
                                        **{"mention": message.author.mention}))
        dans = random.randint(0, 600)

        async def spawn_decoy_duck():
            await asyncio.sleep(dans)
            await spawning.spawn_duck(self.bot, ctx.channel)

        asyncio.ensure_future(spawn_decoy_duck())

    @shop.command(name="21", aliases=["bread", "breadcrumbs"])
    @checks.have_exp(2)
    async def item21(self, ctx):
        message = ctx.message
        _ = self.bot._;
        language = await self.bot.db.get_pref(ctx.guild, "language")
        if random.randint(1, 6) == 1:
            self.bot.ducks_planning[message.channel] += 1
        # TODO : For real, make it !
        # commons.bread[message.channel] += 20
        await self.bot.db.add_to_stat(message.channel, message.author, "exp", -2)

        await self.bot.send_message(ctx=ctx,
                                    message=_(":money_with_wings: You put some bread on the channel to attract ducks. They'll stay 20 seconds longer before leaving for the rest of the day!", language))
        await self.bot.hint(ctx=ctx, message=_(":money_with_wings: Bread can stack! Buy some more to maximise the effects!", language))

    @shop.command(name="22", aliases=["NOT2"])
    @checks.have_exp(5)
    async def shop22(self, ctx):
        raise NotImplementedError

    @shop.command(name="23", aliases=["fake_duck", "mechanical_duck", "mechanical", "fake"])
    @checks.have_exp(40)
    async def item23(self, ctx):
        """Buy a mechanical duck (40 exp)
        !shop 23"""
        message = ctx.message
        _ = self.bot._;
        language = await self.bot.db.get_pref(ctx.guild, "language")

        try:
            await ctx.message.delete()
        except discord.Forbidden:
            await self.bot.hint(ctx=ctx, message=_("If you ask a server admin to give me the `manage_message` permission, I will be able to delete that kind of shop commands ;)", language))
        except discord.NotFound:
            pass

        await self.bot.db.add_to_stat(message.channel, message.author, "exp", -40)
        await self.bot.send_message(ctx=ctx, force_pm=True, message=_(":money_with_wings: You prepared a mechanical duck on the channel for 40 exp. It's wrong, but so funny!", language))

        async def spawn_mech_duck():
            await asyncio.sleep(90)
            duck = await ducks.MechanicalDuck.create(self.bot, ctx.channel, user=ctx.message.author)
            await spawning.spawn_duck(self.bot, ctx.channel, instance=duck, ignore_event=True)

        asyncio.ensure_future(spawn_mech_duck())


def setup(bot):
    bot.add_cog(Experience(bot))
