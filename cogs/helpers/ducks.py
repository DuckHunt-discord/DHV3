"""
In this helper, every kind of duck the bot can spawn is defined.
"""
import logging
import random
import time

class DuckWrapper:
    """Class used to pass a player as an argument to some duck functions in user_commands.py"""
    def __init__(self, duck, shooter):
        self.duck = duck
        self.shooter = shooter

    def __getattr__(self, name, *args, **kwargs):
        """ In case we can't see the function, redirect to the duck object"""
        return getattr(self.duck, name)(self, *args, **kwargs)

    async def frightened(self):
        return await self.duck.frightened(self.shooter)

    async def shoot(self):
        return await self.duck.shoot(self.shooter)


class BaseDuck:
    """
    Just a dummy duck type to highlight the required values a Duck subclass must provide
    """

    def __init__(self, bot, channel):

        self.bot = bot
        self.channel = channel

        self._logger = None

        self.starting_life = 1
        self.life = 1

        self.spawned_at = int(time.time())

        # Optional settings that probably won't get changed often
        self.can_miss = True
        self.can_use_clover = True

        # Dummy values that should be replaced... Probably
        self.exp_value = 0
        self.staying_until = self.spawned_at
        self.discord_spawn_str = "-,_,.-'\`'°-,_,.-'\`'° \\_O< COIN"
        self.discord_leave_str = "·°'\`'°-.,¸¸.·°'\`"

        self.logger.debug(f"{self.__class__.__name__} created -> {self}")


    @property
    def logger(self):
        if not self._logger:
            extra = {"channelid": self.channel.id, "userid": 0}
            self._logger = logging.LoggerAdapter(self.bot.base_logger, extra)

        return self._logger

    @property
    def killed(self):
        if self.life <= 0:
            return True
        else:
            return False

    @property
    def time(self):
        return self.spawned_at

    @classmethod
    async def create(cls, bot, channel, ignore_event=False):
        raise RuntimeError("Trying to create an instance of BaseDuck, or subclass not re-implementing create")

    def delete(self):
        self.bot.ducks_spawned.remove(self)

    async def frightened(self, player):
        _ = self.bot._
        language = await self.bot.db.get_pref(self.channel.guild, "language")

        await self.bot.db.add_to_stat(self.channel, player, "exp", -1)
        try:
            self.delete()
        except ValueError:
            # Duck was removed elsewhere (race condition)
            # Just be like, yup, you missed
            await self.bot.db.add_to_stat(self.channel, player, "shoots_missed", 1)
            return _("**PIEWW**\tYou missed the duck! [missed: -1 xp]", language)

        await self.bot.db.add_to_stat(self.channel, player, "shoots_frightened", 1)
        return _("**FLAPP**\tFrightened by so much noise, the duck fled! CONGRATS! [missed: -1 xp]", language)

    async def _process_super_ammo(self, author):
        channel = self.channel
        now = time.time()
        _ = self.bot._
        language = await self.bot.db.get_pref(self.channel.guild, "language")

        if await self.bot.db.get_stat(channel, author, "explosive_ammo") > int(now):
            self.life -= 3
            vieenmoins = 3
            ono = _("BPAM", language)
        elif await self.bot.db.get_stat(channel, author, "ap_ammo") > int(now):
            self.life -= 2
            vieenmoins = 2
            ono = _("BAAM", language)
        else:
            self.life -= 1
            vieenmoins = 1
            ono = random.choice([_("BOUM", language), _("SPROTCH", language)])

        return vieenmoins, ono

    async def _get_experience_spent(self, author):
        channel = self.channel
        now = time.time()

        # 13a/ Experience
        exp = self.exp_value

        # 13b/ Clover
        trefle = 0
        if await self.bot.db.get_stat(channel, author, "trefle") > now and self.can_use_clover:
            trefle = await self.bot.db.get_stat(channel, author, "trefle_exp")
            await self.bot.db.add_to_stat(channel, author, "exp_won_with_clover", trefle)
            exp += trefle

        # 13c/ Rounding experience
        return int(exp), trefle

    async def _update_best_time_taken(self, author):
        now = time.time()

        # 13e/ Best time
        time_taken = round(now - self.time, 6)
        if await self.bot.db.get_stat(self.channel, author, "best_time") > time_taken:
            await self.bot.db.set_stat(self.channel, author, "best_time", time_taken)

        return time_taken

    async def pre_shoot(self, author):
        pass

    async def post_kill(self, author, exp):
        pass

    async def post_harmed(self, author):
        #Harmed but not killed
        await self.bot.db.add_to_stat(self.channel, author, "shoots_harmed_duck", 1)

    async def shoot(self, author):
        channel = self.channel
        _ = self.bot._
        language = await self.bot.db.get_pref(self.channel.guild, "language")

        await self.pre_shoot(author)

        # 12/ Super ammo
        vieenmoins, ono = await self._process_super_ammo(author)



        # 13/ Duck killed ?
        if self.killed:
            try:
                self.delete()
            except ValueError:
                # Duck was removed elsewhere (race condition)
                # Just be like, yup, you missed
                # It never happen anyway
                # Well, it could but never saw it in real life

                await self.bot.db.add_to_stat(channel, author, "exp", -1)
                await self.bot.db.add_to_stat(channel, author, "shoots_missed", 1)
                await self.bot.db.add_to_stat(channel, author, "shoots_almost_killed", 1)
                return _("That was close, you almost killed the duck, but the other hunter got it first! [missed: -1 xp]", language)


            exp, trefle = await self._get_experience_spent(author)
            # 13d/ Give experience
            await self.bot.db.add_to_stat(channel, author, "exp", exp)
            await self.bot.db.add_to_stat(channel, author, "killed_ducks", 1)

            time_taken = await self._update_best_time_taken(author)

            # 13f/ Communicate

            if trefle == 0:
                exp_str = f"[{exp} exp]"
            else:
                exp_str = f"[{exp - trefle} exp + **{trefle} clover**]"

            await self.post_kill(author, exp)

            return (await self.get_killed_string()).format(
                **{"time": round(time_taken, 4),
                   "total": await self.bot.db.get_stat(channel, author, "killed_ducks"), "channel": channel,
                   "exp": exp_str,
                   "supercanards": await self.bot.db.get_stat(channel, author, "killed_super_ducks"),
                   "onomatopoeia": ono})

        else:
            await self.post_harmed(author)

            return (await self.get_harmed_message()).format(
                **{
                    "vie":vieenmoins,
                    "current_life": self.life,
                    "max_life": self.starting_life
                })

    async def hug(self, ctx):

        author = ctx.author
        _ = self.bot._
        language = await self.bot.db.get_pref(self.channel.guild, "language")
        await self.bot.db.add_to_stat(self.channel, author, "hugged_nohug_ducks", 1)
        await self.bot.db.add_to_stat(self.channel, author, "exp", -2)

        if self.bot.db.get_stat(self.channel, author, "confisque"):
            return _(":heart: You try to hug the duck, but he knows you killed his brother, so he flew away from you, back in the pond! [-2 exp]", language)
        else:
            return _(":heart: You try to hug the duck, but he saw the weapon you hid behind your back, and flew away from you, back in the pond! [-2 exp]", language)

    async def get_frighten_chance(self):
        return await self.bot.db.get_pref(self.channel.guild, "duck_frighten_chance")

    async def get_killed_string(self):
        _ = self.bot._
        language = await self.bot.db.get_pref(self.channel.guild, "language")

        return _(":skull_crossbones: **{onomatopoeia}**\tYou killed the duck in {time} seconds, you are now at a grand total of {total} ducks (of which {supercanards} "
                 "were super-ducks) killed on #{channel}.     \_X<   *COUAC*   {exp}", language)

    async def get_harmed_message(self):
        _ = self.bot._
        language = await self.bot.db.get_pref(self.channel.guild, "language")

        if await self.bot.db.get_pref(self.channel.guild, "show_super_ducks_life"):
            return _(":gun: The duck survived, try again! *SUPER DUCK DETECTED* [life: -{vie} ({current_life} / {max_life})]", language)
        else:
            return _(":gun: The duck survived, try again! *SUPER DUCK DETECTED* [life: -{vie}]", language)



    def __repr__(self):
        now = int(time.time())
        return f"{self.__class__.__name__} spawned {now - self.spawned_at} seconds ago on #{self.channel.name}" \
               f"Life: {self.life} / {self.starting_life}, and an exp value of {self.exp_value}"

    def __str__(self):
        now = int(time.time())
        return f"{self.__class__.__name__} spawned {now - self.spawned_at} seconds ago on #{self.channel.name} @ {self.channel.guild.name}" \
               f"Life: {self.life} / {self.starting_life}, and an exp value of {self.exp_value}"



class Duck(BaseDuck):
    """
    The common duck, with a life of one that can spawn in the game
    """

    def __init__(self, bot, channel, exp, ttl):
        super().__init__(bot, channel)

        self.staying_until = self.spawned_at + ttl
        self.exp_value = exp

    async def _gen_discord_str(self):
        _ = self.bot._
        language = await self.bot.db.get_pref(self.channel.guild, "language")

        trace = random.choice(self.bot.canards_trace)
        corps = await self.bot.db.get_pref(self.channel.guild, "emoji_used")
        cri = _(random.choice(self.bot.canards_cri), language=language)

        self.discord_spawn_str = f"{trace} {corps} < {cri}"
        self.discord_leave_str = _(random.choice(self.bot.canards_bye), language)

    @classmethod
    async def create(cls, bot, channel, ignore_event=False):

        # Base duck time to live
        ttl = await bot.db.get_pref(channel.guild, "time_before_ducks_leave")

        # Base duck exp
        exp_value = await bot.db.get_pref(channel.guild, "exp_won_per_duck_killed")

        duck = cls(bot, channel, exp=exp_value, ttl=ttl)
        await duck._gen_discord_str()
        return duck

    async def post_kill(self, author, exp):
        await self.bot.db.add_to_stat(self.channel, author, "killed_normal_ducks", 1)


class SuperDuck(BaseDuck):
    """
    A special duck with more than one life point
    """

    def __init__(self, bot, channel, life, exp, ttl):
        super().__init__(bot, channel)
        self.staying_until = self.spawned_at + ttl
        self.exp_value = exp

        self.life = life
        self.starting_life = life

    async def _gen_discord_str(self):

        # Same as for the Normal Duck because they shouldn't be distinguished

        _ = self.bot._
        language = await self.bot.db.get_pref(self.channel.guild, "language")

        trace = random.choice(self.bot.canards_trace)
        corps = await self.bot.db.get_pref(self.channel.guild, "emoji_used")
        cri = _(random.choice(self.bot.canards_cri), language=language)

        self.discord_spawn_str = f"{trace} {corps} < {cri}"
        self.discord_leave_str = _(random.choice(self.bot.canards_bye), language)

    async def post_kill(self, author, exp):
        await self.bot.db.add_to_stat(self.channel, author, "killed_super_ducks", 1)


    @classmethod
    async def create(cls, bot, channel, ignore_event=False):
        # Base duck time to live
        ttl = await bot.db.get_pref(channel.guild, "time_before_ducks_leave")

        # Base duck exp
        exp_value = await bot.db.get_pref(channel.guild, "exp_won_per_duck_killed")

        # Super duck life
        min_life = await bot.db.get_pref(channel.guild, "super_ducks_minlife")
        max_life = await bot.db.get_pref(channel.guild, "super_ducks_maxlife")

        # Choosen life for this one
        life = random.randint(min(min_life, max_life), max(min_life, max_life))
        if not ignore_event and bot.current_event['id'] == 7:
            life += bot.current_event['life_to_add']

        # Choosen exp for this life
        exp_value = int(exp_value * await bot.db.get_pref(channel.guild, "super_ducks_exp_multiplier") * life)

        duck = cls(bot, channel, life=life, exp=exp_value, ttl=ttl)
        await duck._gen_discord_str()

        return duck


class MechanicalDuck(BaseDuck):
    """
    Special duck "already killed" just to troll other hunters
    """

    def __init__(self, bot, channel, ttl=30, user=None):
        self.user = user
        super().__init__(bot, channel)
        self.life = 1
        self.exp_value = -1
        self.staying_until = self.spawned_at + ttl
        self.can_miss = False
        self.can_use_clover = False

    @property
    def user_name(self):
        if self.user:
            return self.user.name + "#" + self.user.discriminator
        else:
            return None

    @property
    def user_mention(self):
        if self.user:
            return self.user.mention
        else:
            return None


    async def _gen_discord_str(self):

        # Same as for the Normal Duck because they shouldn't be distinguished

        _ = self.bot._
        language = await self.bot.db.get_pref(self.channel.guild, "language")
        guild = self.channel.guild

        trace = random.choice(self.bot.canards_trace) if await self.bot.db.get_pref(self.channel.guild, "randomize_mechanical_ducks") >= 1 else "-_-'\`'°-_-.-'\`'°"
        corps = await self.bot.db.get_pref(self.channel.guild, "emoji_used") if await self.bot.db.get_pref(self.channel.guild, "randomize_mechanical_ducks") >= 2 else await self.bot.db.get_pref(
            self.channel.guild, "emoji_used") # TODO : Insert here a proper Mechanical Duck Emoji!
        cri = _(random.choice(self.bot.canards_cri), language=language) if await self.bot.db.get_pref(self.channel.guild, "randomize_mechanical_ducks") >= 3 else "*BZAACK*"

        self.discord_spawn_str = f"{trace} {corps} < {cri}"

        self.discord_leave_str = None

    @classmethod
    async def create(cls, bot, channel, ignore_event=False, user=None):
        duck = cls(bot, channel, user=user)
        await duck._gen_discord_str()
        return duck

    async def get_killed_string(self):
        _ = self.bot._
        language = await self.bot.db.get_pref(self.channel.guild, "language")

        return _("You have been tricked by {user_mention} to kill a mechanical duck. It obviouly won't work, and you lost 1 exp for this missed shot", language).format(user_mention = self.user_mention)


    async def get_frighten_chance(self):
        return 0

    def __repr__(self):
        now = int(time.time())
        return f"Mechanical Duck spawned {now - self.spawned_at} seconds ago on #{self.channel.name}" \
               f"Made by {self.user_name}"

    def __str__(self):
        now = int(time.time())
        return f"Mechanical Duck spawned {now - self.spawned_at} seconds ago on #{self.channel.name} @ {self.channel.guild.name}" \
               f"Made by {self.user_name}"

    async def post_kill(self, author, exp):
        await self.bot.db.add_to_stat(self.channel, author, "killed_mechanical_ducks", 1)


class BabyDuck(BaseDuck):
    """
    A duck that you shouldn't kill because you'll loose exp if you do
    """

    def __init__(self, bot, channel, exp, ttl):
        super().__init__(bot, channel)

        self.staying_until = self.spawned_at + ttl
        self.exp_value = exp
        self.can_use_clover = False


    async def _gen_discord_str(self):
        _ = self.bot._
        language = await self.bot.db.get_pref(self.channel.guild, "language")

        trace = random.choice(self.bot.canards_trace)
        corps = random.choice(["<:BabyDuck_01:439546718263050241>", "<:BabyDuck_02:439551472762355724>", " <:official_BabyDuck_01:439546718527160322>"])
        cri   = "**COIN**"

        self.discord_spawn_str = f"{trace} {corps} < {cri}"
        self.discord_leave_str = _("The baby duck left looking for some sleep ·°'\`'°-.,¸¸.·°'\`", language)

    @classmethod
    async def create(cls, bot, channel, ignore_event=False):

        # Base duck time to live
        ttl = await bot.db.get_pref(channel.guild, "time_before_ducks_leave")

        # Base duck exp
        exp_value = - await bot.db.get_pref(channel.guild, "exp_won_per_duck_killed")

        duck = cls(bot, channel, exp=exp_value, ttl=ttl)
        await duck._gen_discord_str()
        return duck

    async def get_killed_string(self):
        _ = self.bot._
        language = await self.bot.db.get_pref(self.channel.guild, "language")

        return _(":skull_crossbones: **{onomatopoeia}**\tYou killed the baby duck in {time} seconds, and you shouldn't have done this!"
                 " You'll lose some exp, because you shouldn't kill babies"
                 "\_X<   *COUAC*   {exp}", language)

    async def post_kill(self, author, exp):
        await self.bot.db.add_to_stat(self.channel, author, "killed_baby_ducks", 1)

    async def hug(self, ctx):
        _ = self.bot._
        language = await self.bot.db.get_pref(self.channel.guild, "language")
        author = ctx.author
        await self.bot.db.add_to_stat(self.channel, author, "hugged_baby_ducks", 1)
        await self.bot.db.add_to_stat(self.channel, author, "exp", 3)
        self.delete()
        return _("<:cmd_Hug_01:442695336348221451> **SMACK**\tYou hugged the baby duck, and now it is really happy! [3 exp]\n"
                 "The baby duck left, feeling loved", language)

class MotherOfAllDucks(SuperDuck):

    async def _gen_discord_str(self):
        _ = self.bot._
        language = await self.bot.db.get_pref(self.channel.guild, "language")

        trace = random.choice(self.bot.canards_trace)
        corps = await self.bot.db.get_pref(self.channel.guild, "emoji_used")
        cri   = "**I AM...** Your mother"

        self.discord_spawn_str = f"{trace} {corps} < {cri}"
        self.discord_leave_str = _(random.choice(self.bot.canards_bye), language)


    async def get_killed_string(self):
        _ = self.bot._
        language = await self.bot.db.get_pref(self.channel.guild, "language")
        return _(":skull_crossbones: **{onomatopoeia}**\t You killed me in {time} seconds, but you won't kill my children! \_X<   *COUAC*   {exp}", language)


    async def post_kill(self, author, exp):
        await self.bot.db.add_to_stat(self.channel, author, "killed_mother_of_all_ducks", 1)

        from cogs import spawning
        self.logger.info("A mother of all ducks were killed, spawning two new ducks! ")
        await spawning.spawn_duck(self.bot, self.channel)
        await spawning.spawn_duck(self.bot, self.channel)
