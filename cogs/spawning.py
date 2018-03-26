import asyncio
import datetime
import logging
import random

import time

import discord

MINUTE = 60
HOUR = MINUTE * 60
DAY = HOUR * 24


class Duck:
    def __init__(self, bot, channel, super_duck, life, exp, ttl):
        self.channel = channel
        self.is_super_duck = super_duck
        self.starting_life = life
        self.life = self.starting_life
        self.spawned_at = int(time.time())

        self.staying_until = self.spawned_at + ttl
        self.exp_value = exp

    @property
    def killed(self):
        if self.life <= 0:
            return True
        else:
            return False

    @property
    def time(self):
        return self.spawned_at

    def __repr__(self):
        now = int(time.time())
        kind = "Super duck" if self.is_super_duck else "Duck"
        return f"{kind} spawned {now - self.spawned_at} seconds ago on {self.channel.id}. " \
               f"Life: {self.life} / {self.starting_life}, and an exp value of {self.exp_value}"

    def __str__(self):
        now = int(time.time())
        kind = "Super duck" if self.is_super_duck else "Duck"
        return f"{kind} spawned {now - self.spawned_at} seconds ago on #{self.channel.name} @ {self.channel.guild.name} " \
               f"Life: {self.life} / {self.starting_life}, and an exp value of {self.exp_value}"


async def make_all_ducks_leave(bot):
    bot.logger.info("Bot shutting down")
    bot.can_spawn = False
    for canard in bot.ducks_spawned[:]:
        _ = bot._
        language = await bot.db.get_pref(canard.channel.guild, "language")
        bot.logger.debug(f"Force-leaving of {canard}")
        if canard in bot.ducks_spawned:
            try:
                await bot.send_message(where=canard.channel, can_pm=False, mention=False, message=_(random.choice(bot.canards_bye), language=language), return_message=True)
            except:
                pass

            try:
                bot.ducks_spawned.remove(canard)
            except:
                pass
        else:
            bot.logger.debug(f"{canard} alredy left :)")


async def get_number_of_ducks(total_ducks):
    now = int(time.time())
    thisDay = now - (now % 86400)
    seconds_left = 86400 - (now - thisDay)
    multiplicator = round(seconds_left / 86400, 5)
    if multiplicator == 0:
        multiplicator = 1

    return round(total_ducks * multiplicator)


async def planifie(bot, channel=None, new_day=True):
    if channel:
        total_ducks = await bot.db.get_pref(channel.guild, "ducks_per_day")

        if not new_day:
            total_ducks = await get_number_of_ducks(total_ducks)

        extra = {"channelid": channel.id, "userid": 0}
        logger = logging.LoggerAdapter(bot.base_logger, extra)
        logger.debug(f"(Re-)planning for channel @{total_ducks} ducks left")

        bot.ducks_planning[channel] = total_ducks

    else:
        for channel in await bot.db.list_enabled_channels():
            to_plan_channel = None
            to_plan_guild = bot.get_guild(channel["server"])
            if to_plan_guild:
                to_plan_channel = to_plan_guild.get_channel(channel["channel"])
            if to_plan_channel:
                await planifie(bot, channel=to_plan_channel, new_day=new_day)


async def spawn_duck(bot, channel, super_duck=False, life=1, life_multiplicator=1, ignore_event=False):
    if bot.can_spawn:
        s = time.time()
        _ = bot._
        language = await bot.db.get_pref(channel.guild, "language")
        ttl = await bot.db.get_pref(channel.guild, "time_before_ducks_leave")
        super_ducks_chance = await bot.db.get_pref(channel.guild, "super_ducks_chance")
        exp_value = await bot.db.get_pref(channel.guild, "exp_won_per_duck_killed")

        if not ignore_event and bot.current_event['id'] == 5:
            if random.randint(0, 100) <= bot.current_event['ducks_cancel_chance']:
                bot.logger.debug(f"A duck was canceled due to `connexion problems` (event)")
                return

        if not ignore_event and bot.current_event['id'] == 1:
            if random.randint(0, 100) <= bot.current_event['chance_for_second_duck']:
                await spawn_duck(bot, channel, ignore_event=True)

        chance = random.randint(0, 100)
        if not ignore_event and bot.current_event['id'] == 3:
            chance += bot.current_event['chance_added_for_super_duck']

        if super_duck or chance < super_ducks_chance:
            super_duck = True
            min_life = await bot.db.get_pref(channel.guild, "super_ducks_minlife")
            max_life = await bot.db.get_pref(channel.guild, "super_ducks_maxlife")
            life = life_multiplicator * random.randint(min(min_life, max_life), max(min_life, max_life)) if life == 1 else life
            if not ignore_event and bot.current_event['id'] == 7:
                life += bot.current_event['life_to_add']
            exp_value = exp_value * await bot.db.get_pref(channel.guild, "super_ducks_exp_multiplier") * life

        # bot.logger.debug(f"First checks took {time.time() - s} seconds to return.")

        duck = Duck(bot, channel, super_duck, life, int(exp_value), ttl)

        # bot.logger.debug(f"Duck creation took {time.time() - s} seconds in total.")
        bot.ducks_spawned.append(duck)
        # bot.logger.debug(f"Duck appending took {time.time() - s} seconds in total.")

        if await bot.db.get_pref(channel.guild, "emoji_ducks"):
            corps = await bot.db.get_pref(channel.guild, "emoji_used") + " < "
        else:
            corps = random.choice(bot.canards_trace) + "  " + random.choice(bot.canards_portrait) + "  "

        if await bot.db.get_pref(channel.guild, "randomize_ducks"):
            canard_str = corps + _(random.choice(bot.canards_cri), language=language)
        else:
            canard_str = corps + "QUAACK"

        # bot.logger.debug(f"Pre-duck spawning took {time.time() - s} seconds in total for {duck}.")

        await bot.send_message(where=channel, mention=False, can_pm=False, message=canard_str)

        # bot.logger.debug(f"It took {time.time() - s} seconds to spawn this duck.")
        bot.logger.debug(f"New duck : {duck}")
    else:
        return


async def event_gen(bot, force=False):
    bot.logger.info("One hour passed, we have to remove the previous event, and find a new one (maybe)")
    bot.current_event = next((item for item in bot.event_list if item['id'] == 0), None)  # Reset the event

    if force or random.randint(0, 100) <= 10:
        bot.logger.debug("[EVENT] A new event will be selected")
        event_id = random.randrange(1, len(bot.event_list))
        bot.logger.info(f"[EVENT] Selected event : {event_id}")
        bot.current_event = next((item for item in bot.event_list if item['id'] == event_id), None)  # Reset the event
        bot.logger.info(f"[EVENT] Selected event : {bot.current_event['name']}")
    else:
        bot.logger.info("[EVENT] No new event, see you next time!")

    bot.logger.debug("[EVENT] Updating playing status")
    game = discord.Game(name=f"{bot.current_event['name']}")
    await bot.change_presence(status=discord.Status.online, activity=game)
    bot.logger.debug("[EVENT] Done :)")


async def background_loop(bot):
    bot.logger.debug("Hello from the BG loop, waiting to be ready")
    await bot.wait_until_ready()
    bot.logger.debug("Hello from the BG loop, now ready")
    await event_gen(bot)
    planday = 0
    last_iter = int(time.time())
    last_hour = 0
    try:
        while not bot.is_closed() and bot.can_spawn:
            # bot.logger.debug("Looping")
            now = int(last_iter + 1)
            thisDay = now - (now % DAY)
            seconds_left = int(DAY - (now - thisDay))

            if int((now - 1) / DAY) != planday:
                # database.giveBack(logger)
                if planday == 0:
                    new_day = False
                else:
                    new_day = True
                planday = int(int(now - 1) / DAY)
                await planifie(bot, new_day=new_day)
                last_iter = int(time.time())

            if last_hour < int(int(now / 60) / 60):
                last_hour = int(int(now / 60) / 60)

            if int(now) % 60 == 0:
                bot.logger.info("Current ducks: {canards}".format(**{"canards": len(bot.ducks_spawned)}))

            if int(now) % 3600 == 0:
                await event_gen(bot)

            thishour = int((now % DAY) / HOUR)
            for channel in list(bot.ducks_planning.keys()):

                # Ici, on est au momement ou la logique s'opere:
                # Si les canards ne dorment jamais, faire comme avant, c'est à dire
                # prendre un nombre aléatoire entre 0 et le nombre de secondes restantes avec randrange
                # et le comparer au nombre de canards restants à faire apparaitre dans la journée
                #
                # Par contre, si on est dans un serveur ou les canards peuvent dormir (==)
                # sleeping_ducks_start != sleeping_ducks_stop, alors par exemple :
                # 00:00 |-----==========---------| 23:59 (= quand les canards dorment)
                # dans ce cas, il faut juste modifier la valeur de seconds_left pour enlever le nombre d'heure
                # (en seconde) afin d'augmenter la probabilité qu'un canard apparaisse pendant le reste de la journée
                sdstart = await bot.db.get_pref(channel.guild, "sleeping_ducks_start")
                sdstop = await bot.db.get_pref(channel.guild, "sleeping_ducks_stop")
                currently_sleeping = False

                if sdstart != sdstop:  # Dans ce cas, les canards dorment peut-etre!

                    # logger.debug("This hour is {v} UTC".format(v=thishour))
                    # Bon, donc comptons le nombre d'heures / de secondes en tout ou les canards dorment
                    if sdstart < sdstop:  # 00:00 |-----==========---------| 23:59
                        if thishour < sdstop:
                            sdseconds = (sdstop - sdstart) * HOUR
                        else:
                            sdseconds = 0
                        if sdstart <= thishour < sdstop:
                            currently_sleeping = True
                    else:  # 00:00 |====--------------======| 23:59
                        sdseconds = (24 - sdstart) * HOUR  # Non, on ne compte pas les autres secondes, car elles seront passées
                        if thishour >= sdstart or thishour < sdstop:
                            currently_sleeping = True
                else:
                    sdseconds = 0

                if not currently_sleeping:
                    sseconds_left = seconds_left - sdseconds  # Don't change seconds_left, it's used for others channels
                    if sseconds_left <= 0:
                        extra = {"channelid": channel.id, "userid": 0}
                        logger = logging.LoggerAdapter(bot.base_logger, extra)
                        logger.warning(f"Huh, sseconds_left est à {sseconds_left}... C'est problématique.\n"
                                       f"sdstart={sdstart}, sdstop={sdstop}, thishour={thishour}, sdseconds={sdseconds}, seconds_left={seconds_left}")
                        sseconds_left = 1

                    try:
                        if random.randrange(0, sseconds_left) < bot.ducks_planning[channel]:
                            bot.ducks_planning[channel] -= 1
                            await spawn_duck(bot, channel)
                    except KeyError:  # Race condition
                        # for channel in list(commons.ducks_planned.keys()): <= channel not deleted, so in this list
                        #    if random.randrange(0, seconds_left) < commons.ducks_planned[channel]: <= Channel had been deleted, so keyerror
                        pass

            for duck in bot.ducks_spawned:
                if duck.staying_until < now:  # Canard qui se barre
                    _ = bot._
                    language = await bot.db.get_pref(duck.channel.guild, "language")
                    extra = {"channelid": duck.channel.id, "userid": 0}
                    logger = logging.LoggerAdapter(bot.base_logger, extra)
                    logger.debug(f"A duck is leaving : {duck}")

                    try:
                        await duck.channel.send(_(random.choice(bot.canards_bye), language))
                    except Exception as e:
                        logger.debug(f"I couldn't get a duck to leave : {duck} failed with {e}")

                    try:
                        bot.ducks_spawned.remove(duck)
                    except ValueError:
                        logger.debug(f"Race condiction on removing {duck}")

                        pass

            now = time.time()
            bot.logger.debug("On schedule : " + str(last_iter + 1 - now))

            if last_iter + 1 <= now:
                if last_iter + 1 <= now - 5:
                    bot.logger.warning("Running behind schedule ({s} seconds)... Server overloaded or clock changed?".format(s=str(float(float(last_iter + 1) - int(now)))))
            else:
                await asyncio.sleep(last_iter + 1 - now)

            last_iter += 1
    except KeyboardInterrupt:
        raise
    except Exception as e:
        bot.logger.exception("Fatal Exception")
        raise
