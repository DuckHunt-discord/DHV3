import asyncio
import datetime
import logging
import random

import time

import dateutil.easter
import discord

from cogs.helpers import ducks

MINUTE = 60
HOUR = MINUTE * 60
DAY = HOUR * 24


async def make_all_ducks_leave(bot):
    bot.logger.info("Bot shutting down")
    bot.can_spawn = False
    s = len(bot.ducks_spawned)
    i = 0
    for canard in bot.ducks_spawned[:]:
        i += 1
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
            print(str(i) + "/" + str(s))
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
        permissions_wanted = discord.Permissions.none()
        permissions_wanted.read_messages = True
        permissions_wanted.send_messages = True

        try:
            permissions_okay = channel.permissions_for(channel.guild.me).is_superset(permissions_wanted)
        except AttributeError:
            # Channel was deleted right then
            permissions_okay = False

        if not permissions_okay:
            # Remove the channel, cant send or write messages.
            bot.logger.info(f"Removing channel as we have no I/O perms there.")
            await bot.db.disable_channel(channel)

            bot.ducks_planning.pop(channel, None)

            for duck in bot.ducks_spawned[:]:
                if duck.channel == channel:
                    duck.delete()

            return

        total_ducks = await bot.db.get_pref(channel.guild, "ducks_per_day")

        if not new_day:
            total_ducks = await get_number_of_ducks(total_ducks)

        extra = {"channelid": channel.id, "userid": 0}
        logger = logging.LoggerAdapter(bot.base_logger, extra)
        logger.debug(f"(Re-)planning for channel @{total_ducks} ducks left")

        bot.ducks_planning[channel] = total_ducks
        return total_ducks

    else:
        total_global_ducks = 0
        channel_count = 0
        for channel in await bot.db.list_enabled_channels():
            to_plan_channel = None
            to_plan_guild = bot.get_guild(channel["server"])
            if to_plan_guild:
                to_plan_channel = to_plan_guild.get_channel(channel["channel"])
            if to_plan_channel:
                x = await planifie(bot, channel=to_plan_channel, new_day=new_day)
                total_global_ducks += x if x else 0
                channel_count += 1 if x else 0

        await bot.log(level=30, title="New planification task done", message=f"{total_global_ducks} ducks are planned for today in {channel_count} channels.", where=None)


async def spawn_duck(bot, channel, instance=None, ignore_event=False):
    if bot.can_spawn:
        if not ignore_event and bot.current_event['id'] == 5:
            if random.randint(0, 100) <= bot.current_event['ducks_cancel_chance']:
                bot.logger.debug(f"A duck was canceled due to `connexion problems` (event)")
                return False

        if not ignore_event and bot.current_event['id'] == 1:
            if random.randint(0, 100) <= bot.current_event['chance_for_second_duck']:
                await spawn_duck(bot, channel, ignore_event=True)

        if not instance:

            population = [ducks.Duck, ducks.SuperDuck, ducks.BabyDuck, ducks.MotherOfAllDucks, ]

            weights = [await bot.db.get_pref(channel.guild, "ducks_chance"), await bot.db.get_pref(channel.guild, "super_ducks_chance"),  # Modified below by event n°3
                await bot.db.get_pref(channel.guild, "baby_ducks_chance"), await bot.db.get_pref(channel.guild, "mother_of_all_ducks_chance"), ]

            if not ignore_event and bot.current_event['id'] == 3:
                weights[1] += int(weights[1] * bot.current_event['chance_added_for_super_duck'] / 100)

            if sum(weights) == 0:
                extra = {"channelid": channel.id, "userid": 0}
                logger = logging.LoggerAdapter(bot.base_logger, extra)
                logger.debug("A duck was ignored because all the weights were set to 0")
                # Owner don't want ducks to spawn
                return False

            type_ = random.choices(population, weights=weights, k=1)[0]

            instance = await type_.create(bot, channel, ignore_event=ignore_event)

        bot.ducks_spawned.append(instance)

        message = instance.discord_spawn_str

        if await bot.db.get_pref(channel.guild, "debug_show_ducks_class_on_spawn"):
            message = f"[{type(instance).__name__}] -- {message}"

        await bot.send_message(where=channel, mention=False, can_pm=False, message=message)
    else:
        return False


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
        # await bot.log(level=9, title="No new event rolled out", message=f"No event active until the next hour", where=None)

        bot.logger.info("[EVENT] No new event, see you next time!")

    bot.logger.debug("[EVENT] Updating playing status")
    game = discord.Game(name=f"{bot.current_event['name']}")
    await bot.log(level=10, title="New event rolled out", message=f"{bot.current_event['name']} is now the active event until the next hour", where=None)

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
                    duck.logger.debug(f"A duck is leaving : {duck}")

                    try:
                        if duck.discord_leave_str:
                            await bot.send_message(where=duck.channel, can_pm=False, mention=False, message=duck.discord_leave_str)
                    except Exception as e:
                        duck.logger.debug(f"I couldn't get a duck to leave : {duck} failed with {e}")

                    try:
                        bot.ducks_spawned.remove(duck)
                    except ValueError:
                        duck.logger.debug(f"Race condiction on removing {duck}")

                        pass

            n = datetime.datetime.now()

            april_fools = n.day == 1 and n.month == 4

            # Fake ducks
            if april_fools:
                random_channel = random.choice(list(bot.ducks_planning.keys()))
                emoji = random.choice([":blowfish:", "🦞", ":shark:", ":octopus:", ":dolphin:" , ":squid:",  ":whale:", ":tropical_fish:", ":whale2:", "❥᷁)͜͡˒ ⋊"])
                try:
                    await bot.send_message(where=random_channel, can_pm=False, mention=False, message=f"-,..,.-'\`'°-,_,.-'\`'° {emoji} < **G**lub **G**lub")
                except Exception as e:
                    logger.exception("Couldn't send an april fool duck")


            now = time.time()
            # bot.logger.debug("On schedule : " + str(last_iter + 1 - now))
            bot.loop_latency = last_iter + 1 - now

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
