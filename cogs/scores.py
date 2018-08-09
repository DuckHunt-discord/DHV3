import argparse
import datetime

import discord
import math

import time
from discord.ext import commands
from discord.ext.commands import BucketType

from cogs.helpers import checks

class Get_Stats:
    def __init__(self, bot, channel, target):
        self.channel = channel
        self.target = target
        self.bot = bot

    async def __call__(self, stat):
        return await self.bot.db.get_stat(self.channel, self.target, stat)


class Scores:
    def __init__(self, bot):
        self.bot = bot

    async def objectTD(self, gs, object):
        date_expiration = datetime.datetime.fromtimestamp(await gs(object))
        td = date_expiration - datetime.datetime.now()
        _ = gs.bot._
        language = await self.bot.db.get_pref(gs.channel.guild, "language")

        return _("{date} (in {dans_jours}{dans_heures} and {dans_minutes})", language).format(
            **{"date": date_expiration.strftime(_('%m/%d at %H:%M:%S', language)),
               "dans_jours": _("{dans} days ", language).format(**{"dans": td.days}) if td.days else "",
               "dans_heures": _("{dans} hours", language).format(**{"dans": td.seconds // 3600}),
               "dans_minutes": _("{dans} minutes", language).format(**{"dans": (td.seconds // 60) % 60})})



    @commands.command(aliases=["topscores", "leaderboard", "top_scores"])
    @checks.is_channel_enabled()
    @commands.cooldown(3, 60, BucketType.channel)
    async def top(self, ctx, *, args: str = ""):
        message = ctx.message
        channel = message.channel
        _ = self.bot._
        language = await self.bot.db.get_pref(ctx.guild, "language")



        await self.bot.send_message(ctx=ctx, message=_("The scores are online at http://duckhunt.api-d.com/web/duckstats.php?cid={channel_id}", language).format(
            channel_id=channel.id))
        # await self.bot.hint(ctx=ctx, message="The following will disappear in a few days. If you notice a bug, please report it on the DuckHunt server : <https://discord.gg/G4skWae>. Thanks! ")

        # Old version of the command
        """

        args = args.split()
        parser = argparse.ArgumentParser(description='Parse the top command.')
        # parser.add_argument('--show', dest='count', type=int, default=10)

        parser.add_argument('--sort-by', dest='sort_by', type=str, default="exp", choices=["exp", "killed", "missed", "time"])

        try:
            args = parser.parse_args(args)
        except SystemExit:
            await self.bot.hint(ctx=ctx, message=_("You have to use `--sort-by [exp/killed/missed/time]` here.", language))
            return



        permissions = channel.permissions_for(message.guild.me)

        available_stats = {
            'exp': {
                'name': _('Exp points', language),
                'key' : 'exp'
            },
            'killed': {
                'name': _('Ducks killed', language),
                'key' : 'killed_ducks'
            },
            'missed': {
                'name': _('Shots missed', language),
                'key' : 'shoots_missed'
            },
            'time': {
                'name': _('Best time', language),
                'key': 'best_time',
            }
        }


        sorting_field = available_stats[args.sort_by]
        additional_field = available_stats['exp' if sorting_field['key'] is not 'exp' else 'killed']

        if not permissions.read_messages \
                or not permissions.manage_messages \
                or not permissions.embed_links \
                or not permissions.read_message_history:

            await self.bot.send_message(ctx=ctx, message=_("Can't post embeds!", language))
            await self.bot.hint(ctx, _("Use `dh!setup` to see missing permissions and ask an admin to give me the missing ones!", language))


            return

        else:
            # \N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR} is >>|
            # \N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR} is |<<

            reaction = True
            changed = True

            first_page_emo = "\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}"
            prev_emo = "\N{BLACK LEFT-POINTING TRIANGLE}"
            next_emo = "\N{BLACK RIGHT-POINTING TRIANGLE}"
            last_page_emo = "\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}"

            topscores = await self.bot.db.top_scores(channel=channel, sorted_by=sorting_field['key'], second_sort_by=additional_field['key'])

            reaction_list = []
            if len(topscores) > 10:
                reaction_list = [next_emo, last_page_emo]

            current_page = 1

            message = await self.bot.send_message(ctx=ctx, message=_("Generating top scores for your channel, please wait!", language), force_pm=await self.bot.db.get_pref(ctx.guild, "pm_stats"),
                                                  return_message=True)

            while reaction:
                if changed:
                    # channel:discord.TextChannel
                    i = current_page * 10 - 10

                    scores_to_process = topscores[i:i + 10]

                    if scores_to_process:
                        embed = discord.Embed(description="Page #{i}".format(i=current_page))
                        embed.title = _(":cocktail: Best scores for {channel_name} :cocktail:", language).format(**{
                            "channel_name": channel.name,
                        })

                        embed.colour = discord.Colour.green()
                        # embed.timestamp = datetime.datetime.now()
                        embed.url = 'https://duckhunt.me/'  # TODO: get the webinterface url and add it here inplace

                        players_list = ""
                        first_stat_list = ""
                        additional_stat_list = ""

                        for joueur in scores_to_process:

                            joueur = dict(joueur)
                            i += 1

                            if (not "killed_ducks" in joueur) or (not joueur["killed_ducks"]):
                                joueur["killed_ducks"] = _("None!", language)

                            if sorting_field['key'] is 'best_time':
                                best_time = round(joueur.get('best_time', None) or 0, 3)
                                joueur['best_time'] = int(best_time) if int(best_time) == float(best_time) else float(best_time)

                            if (not "best_time" in joueur) or (not joueur["best_time"]):
                                joueur["best_time"] = _('None!', language)

                            member = ctx.message.guild.get_member(joueur["id_"])

                            player_name = joueur['name'] if len(joueur['name']) <= 10 else joueur['name'][:9] + '…'
                            player_name = member.name if member else player_name
                            if await self.bot.db.get_pref(ctx.guild, "mention_in_topscores"):
                                # mention = mention if len(mention) < 20 else joueur["name"]
                                mention = member.mention if member else player_name
                            else:
                                mention = player_name

                            players_list += "#{i} {name}".format(name=mention, i=i) + "\n\n"
                            first_stat_list += str(joueur.get(sorting_field['key'], None) or 0) + "\n\n"
                            additional_stat_list += str(joueur.get(additional_field['key'], None) or 0) + "\n\n"

                        embed.add_field(name=_("Player", language), value=players_list, inline=True)
                        embed.add_field(name=sorting_field['name'], value=first_stat_list, inline=True)
                        embed.add_field(name=additional_field['name'], value=additional_stat_list, inline=True)

                        try:
                            await message.edit(content="<:official_Duck_01:439546719177539584>", embed=embed)
                        except discord.errors.Forbidden:
                            await self.bot.send_message(ctx=ctx, message=_(":warning: There was an error while sending the embed, "
                                                                           "please check if the bot has the `embed_links` permission and try again!", language))

                        for emo in reaction_list:
                            await message.add_reaction(emo)

                        changed = False

                if reaction_list:
                    def check(reaction, user):
                        cond = reaction.message.id == message.id
                        cond = cond and user == ctx.message.author
                        cond = cond and str(reaction.emoji) in reaction_list
                        return cond

                    try:
                        res = await self.bot.wait_for('reaction_add', check=check, timeout=1200)
                    except:
                        res = None
                        pass

                    if res:
                        reaction, user = res
                        emoji = reaction.emoji
                        reaction_list = []
                        changed = True

                        if emoji == first_page_emo:
                            current_page = 1
                            reaction_list.extend([next_emo, last_page_emo])
                        elif emoji == prev_emo:
                            current_page -= 1
                            if ((current_page * 10) - 10) > 0:
                                reaction_list.extend([first_page_emo, prev_emo])
                            reaction_list.extend([next_emo, last_page_emo])
                        elif emoji == next_emo:
                            current_page += 1
                            reaction_list.extend([first_page_emo, prev_emo])
                            if len(topscores) > current_page * 10:
                                reaction_list.extend([next_emo, last_page_emo])
                        elif emoji == last_page_emo:
                            current_page = math.ceil(len(topscores) / 10)
                            reaction_list.extend([first_page_emo, prev_emo])

                        try:
                            await message.clear_reactions()
                        except discord.errors.Forbidden:
                            #await self.bot.send_message(ctx=ctx, message=_("I don't have the `manage_messages` permission, I can't remove reactions. Please tell an admin. ;)", language))
                            pass
                    else:
                        reaction = False
                else:
                    reaction = False
"""


    @commands.command(aliases=["stats", "duck_stats"])
    @checks.is_channel_enabled()
    @commands.cooldown(2, 60, BucketType.user)
    @checks.had_giveback()
    async def duckstats(self, ctx, target: discord.Member=None):

        message = ctx.message
        channel = message.channel
        _ = self.bot._
        language = await self.bot.db.get_pref(ctx.guild, "language")

        if not target:
            target = ctx.message.author

        await self.bot.send_message(ctx=ctx, message=_("Your duckstats are waiting for you at http://duckhunt.api-d.com/web/duckstats.php?cid={channel_id}&pid={player_id}", language).format(
            channel_id=ctx.channel.id, player_id=target.id))
        #await self.bot.hint(ctx=ctx, message="The following will disappear in a few days. If you notice a bug, please report it on the DuckHunt server : <https://discord.gg/G4skWae>. Thanks! ")

        # Old version of the command
        """

        gs = Get_Stats(self.bot, channel, target)

        level = await self.bot.db.get_level(channel=channel, player=target)
        reaction = True
        changed = True

        next_emo = "\N{BLACK RIGHT-POINTING TRIANGLE}"
        prev_emo = "\N{BLACK LEFT-POINTING TRIANGLE}"
        first_page_emo = "\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}"

        current_page = 1
        total_page = 4

        duckstats_message = await self.bot.send_message(ctx=ctx, force_pm=await self.bot.db.get_pref(ctx.guild, "pm_stats"),
                                                        message=_("Generating DuckHunt statistics for you, please wait...", language), return_message=True)
        await duckstats_message.add_reaction(first_page_emo)
        await duckstats_message.add_reaction(prev_emo)
        await duckstats_message.add_reaction(next_emo)

        while reaction:
            if changed:
                embed = discord.Embed(description=_("Page {current}/{max}", language).format(current=current_page, max=total_page))

                if await gs("confisque"):
                    embed.description += _("\nConfiscated weapon!", language)

                embed.set_author(name=str(target), icon_url=target.avatar_url)
                embed.set_thumbnail(url=target.avatar_url if target.avatar_url else self.bot.user.avatar_url)
                embed.url = 'https://duckhunt.me/'
                embed.colour = discord.Colour.green()
                embed.set_footer(text='DuckHunt V3', icon_url='http://api-d.com/snaps/2016-11-19_10-38-54-q1smxz4xyq.jpg')

                if current_page == 1:
                    embed.title = _("General statistics", language)

                    best_time = await gs("best_time")
                    if best_time:
                        best_time = int(best_time) if int(best_time) == float(best_time) else float(best_time)
                    else:
                        best_time = _('No best time.', language)

                    if await gs("killed_ducks") > 0:
                        ratio = round(await gs("exp") / await gs("killed_ducks"), 4)
                    else:
                        ratio = _("No duck killed", language)

                    embed.add_field(name=_("Ducks killed", language), value=str(await gs("killed_ducks")))
                    embed.add_field(name=_("Super ducks killed", language), value=str(await gs("killed_super_ducks")))
                    embed.add_field(name=_("Players killed", language), value=str(await gs("killed_players")))
                    embed.add_field(name=_("Self-killing shots", language), value=str(await gs("self_killing_shoots")))

                    embed.add_field(name=_("Best killing time", language), value=str(best_time))
                    embed.add_field(name=_("Bullets in current magazine", language), value=str(await gs("balles")) + " / " + str(level["balles"]))
                    embed.add_field(name=_("Exp points", language), value=str(await gs("exp")))
                    embed.add_field(name=_("Ratio (exp/ducks killed)", language), value=str(ratio))
                    embed.add_field(name=_("Current level", language), value=str(level["niveau"]) + " (" + _(level["nom"], language) + ")")
                    embed.add_field(name=_("Shots accuracy", language), value=str(level["precision"]))
                    embed.add_field(name=_("Weapon reliability", language), value=str(level["fiabilitee"]))
                elif current_page == 2:
                    embed.title = _("Shoots statistics", language)

                    embed.add_field(name=_("Shots fired", language), value=str(await gs("shoots_fired")))
                    embed.add_field(name=_("Shots missed", language), value=str(await gs("shoots_missed")))
                    embed.add_field(name=_("Shots without ducks", language), value=str(await gs("shoots_no_duck")))
                    embed.add_field(name=_("Shots that frightened a duck", language), value=str(await gs("shoots_frightened")))
                    embed.add_field(name=_("Shots that harmed a duck", language), value=str(await gs("shoots_harmed_duck")))
                    embed.add_field(name=_("Shots stopped by the detector", language), value=str(await gs("shoots_infrared_detector")))
                    embed.add_field(name=_("Shots jamming a weapon", language), value=str(await gs("shoots_jamming_weapon")))
                    embed.add_field(name=_("Shots with a sabotaged weapon", language), value=str(await gs("shoots_sabotaged")))
                    embed.add_field(name=_("Shots with a jammed weapon", language), value=str(await gs("shoots_with_jammed_weapon")))
                    embed.add_field(name=_("Shots without bullets", language), value=str(await gs("shoots_without_bullets")))
                    embed.add_field(name=_("Shots without weapon", language), value=str(await gs("shoots_without_weapon")))
                    embed.add_field(name=_("Shots when wet", language), value=str(await gs("shoots_tried_while_wet")))

                elif current_page == 3:
                    embed.title = _("Reloads and items statistics", language)

                    embed.add_field(name=_("Reloads", language), value=str(await gs("reloads")))
                    embed.add_field(name=_("Reloads without magazines", language), value=str(await gs("reloads_without_chargers")))
                    embed.add_field(name=_("Reloads not needed", language), value=str(await gs("unneeded_reloads")))

                    embed.add_field(name=_("Trash found in bushes", language), value=str(await gs("trashFound")))

                    embed.add_field(name=_("Exp earned with a clover", language), value=str(await gs("exp_won_with_clover")))
                    embed.add_field(name=_("Life insurance rewards", language), value=str(await gs("life_insurence_rewards")))
                    embed.add_field(name=_("Free givebacks used", language), value=str(await gs("givebacks")))

                elif current_page == 4:
                    embed.title = _("Possesed items and effects", language)

                    if await gs("graisse") > int(time.time()):
                        embed.add_field(name=_("Object: grease", language), value=str(await self.objectTD(gs, "graisse")))

                    if await gs("detecteurInfra") > int(time.time()):
                        embed.add_field(name=_("Object: infrared detector", language), value=str(await self.objectTD(gs, "detecteurInfra")))

                    if await gs("silencieux") > int(time.time()):
                        embed.add_field(name=_("Object: silencer", language), value=str(await self.objectTD(gs, "silencieux")))

                    if await gs("trefle") > int(time.time()):
                        embed.add_field(name=_("Object: clover {exp} exp", language).format(**{"exp": await gs("trefle_exp")}), value=str(await self.objectTD(gs, "trefle")))

                    if await gs("explosive_ammo") > int(time.time()):
                        embed.add_field(name=_("Object: explosive ammo", language), value=str(await self.objectTD(gs, "explosive_ammo")))
                    elif await gs("ap_ammo") > int(time.time()):
                        embed.add_field(name=_("Object: AP ammo", language), value=str(await self.objectTD(gs, "ap_ammo")))

                    if await gs("mouille") > int(time.time()):
                        embed.add_field(name=_("Effect: wet", language), value=str(await self.objectTD(gs, "mouille")))

                try:
                    #ctx.logger.debug("Duckstats : " + str(embed.to_dict()))
                    await duckstats_message.edit(content="<:official_Duck_01:439546719177539584>", embed=embed)
                    #await self.bot.send_message(ctx=ctx, embed=embed)
                except:
                    ctx.logger.exception("Error sending embed, with embed " + str(embed.to_dict()))
                    await self.bot.send_message(ctx=ctx,
                                                message=_(":warning: There was an error while sending the embed, please check if the bot has the `embed_links` permission and try again!", language))
                    return

                changed = False

            def check(reaction, user):
                cond = reaction.message.id == duckstats_message.id
                cond = cond and user == ctx.message.author
                cond = cond and str(reaction.emoji) in [next_emo, prev_emo, first_page_emo]
                return cond

            try:
                res = await self.bot.wait_for('reaction_add', check=check, timeout=1200)
            except:
                res = None
                #ctx.logger.exception("Can't wait for")
                pass

            if res:
                reaction, user = res
                emoji = reaction.emoji
                if emoji == next_emo:
                    changed = True
                    if current_page == total_page:
                        current_page = 1
                    else:
                        current_page += 1
                    try:
                        await duckstats_message.remove_reaction(emoji, user)
                    except discord.errors.Forbidden:
                        #ctx.logger.exception("Forbidden from duckstats 1") #!duckstats 345315631236907008
                        pass  # await self.bot.send_message(message.channel, _("I don't have the `manage_messages` permissions, I can't remove reactions. Warn an admin for me, please ;)", language))
                elif emoji == prev_emo:
                    changed = True
                    if current_page > 1:
                        current_page -= 1
                    else:
                        current_page = total_page
                    try:
                        await duckstats_message.remove_reaction(emoji, user)
                    except discord.errors.Forbidden:
                        #ctx.logger.exception("Forbidden from duckstats 2")
                        pass  # await self.bot.send_message(message.channel, _("I don't have the `manage_messages` permissions, I can't remove reactions. Warn an admin for me, please ;)", language))
                elif emoji == first_page_emo:
                    if current_page > 1:
                        changed = True
                        current_page = 1
                    try:
                        await duckstats_message.remove_reaction(emoji, user)
                    except discord.errors.Forbidden:
                        #ctx.logger.exception("Forbidden from duckstats 3")
                        pass  # await self.bot.send_message(message.channel, _("I don't have the `manage_messages` permissions, I can't remove reactions. Warn an admin for me, please ;)", language))
            else:
                reaction = False
                try:
                    await message.delete()
                except:
                    ctx.logger.exception("Can't delete message")
                    pass
                return
"""

def setup(bot):
    bot.add_cog(Scores(bot))
