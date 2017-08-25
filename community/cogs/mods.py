# -*- coding: utf-8 -*-
# !/usr/bin/env python3.5

"""

"""
import argparse
import asyncio
import datetime
import json
import re
import shlex
import time
from collections import Counter

import discord
from discord import InvalidArgument
from discord.ext import commands

from cogs import checks
from cogs.checks import get_level

default_reason = "**No reason provided**, use c!mod reason <case> <reason>."


class Mods:
    def __init__(self, bot):
        self.bot = bot
        self.root_dir = self.bot.where + "/mods/"

    async def add_action(self, user: discord.User, action: str, by: discord.user, reason: str = default_reason, announce=True):
        """
        Save an action done by a mod to the filesystem.
        :param user: "Victim user"
        :param action: Action applied on the user, for example "ban"
        :param by: Moderator that used the command
        :param reason: Reason given for the action
        :return: The case number assigned to the action
        """
        with open(self.root_dir + "/current_case.txt", "r") as file:
            current_case = int(file.read())
        with open(self.root_dir + "/current_case.txt", "w") as file:
            file.write(str(current_case + 1))

        # USER LOG
        try:
            with open(self.root_dir + "/users/" + str(user.id) + ".json", "r") as infile:
                user_log = json.load(infile)
        except FileNotFoundError:
            user_log = []

        user_log.append(current_case)

        with open(self.root_dir + "/users/" + str(user.id) + ".json", "w") as outfile:
            json.dump(user_log, outfile)

        # CASE LOG

        action_logged = {
            "date"                : int(time.time()),
            "action"              : action,
            "reason"              : reason,
            "moderator_id"        : by.id,
            "moderator_screenname": by.name + "#" + by.discriminator,
            "victim_screenname"   : user.name + "#" + user.discriminator,
            "victim_id"           : user.id,

        }

        with open(self.root_dir + "/cases/" + str(current_case) + ".json", "w") as outfile:
            json.dump(action_logged, outfile)

        if announce:

            embed = await self.get_case_embed(current_case)
            await self.bot.send_message(self.bot.get_channel("317432206920515597"), embed=embed)

        return current_case

    async def get_case_embed(self, case_number: int):
        try:
            with open(self.root_dir + "/cases/" + str(case_number) + ".json") as infile:
                case = json.load(infile)
        except FileNotFoundError:
            return None

        embed = discord.Embed()
        if case["action"] == "Ban":
            embed.colour = discord.Colour.dark_red()
        elif case["action"] == "Unban":
            embed.colour = discord.Colour.green()
        elif case["action"] == "Warn":
            embed.colour = discord.Colour.orange()
        elif case["action"] == "Note":
            embed.colour = discord.Colour.light_grey()
        elif case["action"] == "Mute":
            embed.colour = discord.Colour.orange()
        elif case["action"] == "Unmute":
            embed.colour = discord.Colour.green()
        elif case["action"] == "Deafen":
            embed.colour = discord.Colour.orange()
        elif case["action"] == "Undeafen":
            embed.colour = discord.Colour.green()
        elif case["action"] == "Kick":
            embed.colour = discord.Colour.red()
        else:
            embed.colour = discord.Colour.dark_grey()

        embed.title = "{action} | Case #{case_number}".format(action=case["action"], case_number=case_number)

        # embed.url = "https://api-d.com"
        embed.description = case["reason"]
        embed.add_field(name="Responsible Moderator", value=case["moderator_screenname"] + " (<@" + case["moderator_id"] + ">)", inline=False)
        embed.add_field(name="Victim", value=case["victim_screenname"] + " (<@" + case["victim_id"] + ">)", inline=False)
        embed.timestamp = datetime.datetime.fromtimestamp(case["date"])
        embed.set_author(name=case["victim_id"])

        return embed

    async def list_actions(self, user_id):
        user_id = str(user_id)
        try:
            with open(self.root_dir + "/users/" + str(user_id) + ".json", "r") as infile:
                user_log = json.load(infile)
        except FileNotFoundError:
            user_log = []
        actions = {
            "Kick"    : [],
            "Warn"    : [],
            "Ban"     : [],
            "Unban"   : [],
            "Note"    : [],
            "Mute"    : [],
            "Unmute"  : [],
            "Deafen"  : [],
            "Undeafen": [],
            "total"   : 0
        }

        if user_log:
            for case in user_log:
                with open(self.root_dir + "/cases/" + str(case) + ".json") as infile:
                    case_dict = json.load(infile)
                actions[case_dict["action"]].append(case)
            return actions
        actions["total"] = len(user_log)
        return actions

    async def send_user_log(self, ctx, user_id: str):
        actions = await self.list_actions(user_id)

        await self.bot.send_message(ctx.message.channel,
                                    """{mention} was targeted by mods {total} times. He recived :

                                        - **{kick}** kick(s) {list_kicks},
                                        - **{warns}** warning(s) {list_warns},
                                        - **{bans}** ban(s) {list_bans},
                                        - **{unbans}** unban(s) {list_unbans}

                                    Such a mod abooooose :o
                                    """.format(mention="<@" + user_id + ">",
                                               total=actions["total"],
                                               kick=len(actions["Kick"]),
                                               list_kicks=str(actions["Kick"]) if len(actions["Kick"]) != 0 else "",
                                               warns=len(actions["Warn"]),
                                               list_warns=str(actions["Warn"]) if len(actions["Warn"]) != 0 else "",
                                               bans=len(actions["Ban"]),
                                               list_bans=str(actions["Ban"]) if len(actions["Ban"]) != 0 else "",
                                               unbans=len(actions["Unban"]),
                                               list_unbans=str(actions["Unban"]) if len(actions["Unban"]) != 0 else "",
                                               ))

    async def on_member_ban(self, member):
        case = await self.add_action(user=member, action="Ban", by=self.bot.user)

    async def on_member_unban(self, server, user):
        case = await self.add_action(user=user, action="Unban", by=self.bot.user)

    async def on_message(self, message):
        channel = message.channel
        author = message.author

        if int(channel.id) not in [195260081036591104, 262720111591292928, 195260134908231691]:
            return

        if "invisible" in [x.name.lower() for x in author.roles] or get_level(author) >= 2:
            return

        if author.status is discord.Status.offline:
            fmt = f'{author} (ID: {author.id}) has been automatically blocked for 5 minutes for being invisible'
            # await channel.set_permissions(author, read_messages=False, reason='invisible block')
            overwrite = discord.PermissionOverwrite()
            overwrite.read_messages = False
            await self.bot.edit_channel_permissions(message.channel, message.author, overwrite)
            # await channel.send(fmt)
            await self.bot.send_message(channel, fmt)

            try:
                msg = f'Heya. You have been automatically blocked from <#{channel.id}> for 5 minutes for being ' \
                      'invisible.\nTry chatting again in 5 minutes when you change your status. If you\'re curious ' \
                      'why invisible users are blocked, it is because they tend to break the client and cause them to ' \
                      'be hard to mention. Since we want to help you usually, we expect mentions to work without ' \
                      'headaches.\n\nSorry for the trouble.'
                # await author.send(msg)
                await self.bot.send_message(author, msg)

            except discord.HTTPException:
                pass

            await asyncio.sleep(120)
            # await channel.set_permissions(author, overwrite=None, reason='invisible unblock')
            overwrite.read_messages = None
            await self.bot.edit_channel_permissions(message.channel, message.author, overwrite)
            return

    @commands.group(pass_context=True, aliases=["mod", "stfu"])
    async def moderation(self, ctx):
        pass

    @checks.have_required_level(3)
    @moderation.command(pass_context=True)
    async def reason(self, ctx, case_number: int, *, reason):
        try:
            with open(self.root_dir + "/cases/" + str(case_number) + ".json") as infile:
                case = json.load(infile)

        except FileNotFoundError:
            await self.bot.send_message(ctx.message.channel, "Error: Unknown case ID")
            return None

        case["reason"] = reason
        case["moderator_screenname"] = ctx.message.author.name + "#" + ctx.message.author.discriminator
        case["moderator_id"] = ctx.message.author.id
        with open(self.root_dir + "/cases/" + str(case_number) + ".json", "w") as outfile:
            json.dump(case, outfile)

        await self.bot.send_message(ctx.message.channel, embed=await self.get_case_embed(case_number))

    @checks.have_required_level(3)
    @moderation.command(pass_context=True)
    async def ban(self, ctx, user: discord.User, purge: int = 0, *, reason: str = default_reason):
        """
        Bans a user. This command require multiple arguments
        :param user: The user you would like to ban. Can be a userID, a mention or a username#discrim combo
        :param purge: Purge user messages for X days. Default to 0.
        :param reason: Reason given for the ban.
        :return case_numer: Return the case and the case number.
        """
        await self.bot.ban(user, delete_message_days=purge)
        case = await self.add_action(user=user, action="Ban", by=ctx.message.author, reason=reason)
        embed = await self.get_case_embed(case)
        await self.bot.send_message(ctx.message.channel, embed=embed)

    @checks.have_required_level(3)
    @moderation.command(pass_context=True)
    async def kick(self, ctx, user: discord.Member, purge: int = 5000, *, reason: str = default_reason):
        """
        Bans a user. This command require multiple arguments
        :param user: The user you would like to ban. Can be a userID, a mention or a username#discrim combo
        :param purge: Purge user messages for X messages. Default to 5000.
        :param reason: Reason given for the ban.
        :return case_numer: Return the case and the case number.
        """
        await self.bot.kick(user)

        def is_user(u):
            return u.author == user

        await self.bot.purge_from(ctx.message.channel, limit=purge, check=is_user)

        case = await self.add_action(user=user, action="Kick", by=ctx.message.author, reason=reason)
        embed = await self.get_case_embed(case)
        await self.bot.send_message(ctx.message.channel, embed=embed)
        if len((await self.list_actions(user.id))["Kick"]) >= 5:
            await self.ban.callback(self, ctx, user, 0, reason="Auto ban pour 5+ kicks")

    @checks.have_required_level(3)
    @moderation.command(pass_context=True)
    async def unban(self, ctx, user_str: str, *, reason: str = default_reason):
        """
        Bans a user. This command require multiple arguments
        :param user_str: The user you would like to ban. Can be a userID or a username#discrim combo
        :param reason: Reason given for the unban.
        :return case_numer: Return the case and the case number.
        """
        bans = await self.bot.get_bans(ctx.message.server)
        user = discord.utils.find(lambda m: (str(m.id) == str(user_str)) or (str(m.name + "#" + m.discriminator) == str(user_str)), bans)
        if user:

            await self.bot.unban(ctx.message.server, user)
            case = await self.add_action(user=user, action="Unban", by=ctx.message.author, reason=reason)
            embed = await self.get_case_embed(case)
            await self.bot.send_message(ctx.message.channel, embed=embed)
        else:
            await self.bot.send_message(ctx.message.channel, "User not found :(")

    @checks.have_required_level(3)
    @moderation.command(pass_context=True)
    async def warn(self, ctx, user: discord.User, *, reason: str = default_reason):
        """
        Warns a user. This command require multiple arguments
        :param user: The user you would like to ban. Can be a userID, a mention or a username#discrim combo
        :param reason: Reason given for the warn.
        :return case_numer: Return the case and the case number.
        """
        case = await self.add_action(user=user, action="Warn", by=ctx.message.author, reason=reason)
        embed = await self.get_case_embed(case)
        await self.bot.send_message(ctx.message.channel, embed=embed)
        if len((await self.list_actions(user.id))["Warn"]) >= 5:
            await self.kick.callback(self, ctx, user, 0, reason="Auto kick pour 5+ warns")

    @checks.have_required_level(3)
    @moderation.command(pass_context=True)
    async def note(self, ctx, user: discord.User, *, reason: str = default_reason):
        """
        Warns a user. This command require multiple arguments
        :param user: The user you would like to ban. Can be a userID, a mention or a username#discrim combo
        :param reason: Reason given for the warn.
        :return case_numer: Return the case and the case number.
        """
        case = await self.add_action(user=user, action="Note", by=ctx.message.author, reason=reason)
        embed = await self.get_case_embed(case)
        await self.bot.send_message(ctx.message.channel, embed=embed)

    @checks.have_required_level(3)
    @moderation.command(pass_context=True)
    async def mute(self, ctx, user: discord.Member, *, reason: str = default_reason):
        """
        Mute a user. This command require multiple arguments
        :param user: The user you would like to ban. Can be a userID, a mention or a username#discrim combo
        :param reason: Reason given for the warn.
        :return case_numer: Return the case and the case number.
        """
        await self.bot.server_voice_state(user, mute=True)
        case = await self.add_action(user=user, action="Mute", by=ctx.message.author, reason=reason)
        embed = await self.get_case_embed(case)
        await self.bot.send_message(ctx.message.channel, embed=embed)

    @checks.have_required_level(3)
    @moderation.command(pass_context=True)
    async def unmute(self, ctx, user: discord.Member, *, reason: str = default_reason):
        """
        Unmute a user. This command require multiple arguments
        :param user: The user you would like to ban. Can be a userID, a mention or a username#discrim combo
        :param reason: Reason given for the warn.
        :return case_numer: Return the case and the case number.
        """
        await self.bot.server_voice_state(user, mute=False)
        case = await self.add_action(user=user, action="Unmute", by=ctx.message.author, reason=reason)
        embed = await self.get_case_embed(case)
        await self.bot.send_message(ctx.message.channel, embed=embed)

    @checks.have_required_level(3)
    @moderation.command(pass_context=True)
    async def deafen(self, ctx, user: discord.Member, *, reason: str = default_reason):
        """
        Deafen a user. This command require multiple arguments
        :param user: The user you would like to ban. Can be a userID, a mention or a username#discrim combo
        :param reason: Reason given for the warn.
        :return case_numer: Return the case and the case number.
        """
        await self.bot.server_voice_state(user, deafen=True)
        case = await self.add_action(user=user, action="Deafen", by=ctx.message.author, reason=reason)
        embed = await self.get_case_embed(case)
        await self.bot.send_message(ctx.message.channel, embed=embed)

    @checks.have_required_level(3)
    @moderation.command(pass_context=True)
    async def undeafen(self, ctx, user: discord.Member, *, reason: str = default_reason):
        """
        Warns a user. This command require multiple arguments
        :param user: The user you would like to ban. Can be a userID, a mention or a username#discrim combo
        :param reason: Reason given for the warn.
        :return case_numer: Return the case and the case number.
        """
        await self.bot.server_voice_state(user, deafen=False)
        case = await self.add_action(user=user, action="Undeafen", by=ctx.message.author, reason=reason)
        embed = await self.get_case_embed(case)
        await self.bot.send_message(ctx.message.channel, embed=embed)

    @checks.have_required_level(1)
    @moderation.command(pass_context=True, aliases=["logme", "whatdidido"])
    async def me(self, ctx):
        """
        Get every moderator actions for yourself
        """
        await self.send_user_log(ctx, ctx.message.author.id)

    @checks.have_required_level(2)
    @moderation.command(pass_context=True, aliases=["log", "whodis"])
    async def user_log(self, ctx, user: discord.User):
        """
        Get every moderator actions for a specific user

        :param user: The user you would like to see actions.
        """
        await self.send_user_log(ctx, user.id)

    @checks.have_required_level(2)
    @moderation.command(pass_context=True)
    async def user_logd(self, ctx, user):
        """
        Get every moderator actions for a disconnected user

        :param user: The user you would like to see actions.
        """
        await self.send_user_log(ctx, user)

    @checks.have_required_level(1)
    @moderation.command(pass_context=True, aliases=["view", "hum"])
    async def view_case(self, ctx, case: int):
        """
        View a case using the assotiated case number
        :param case: The case number
        """
        try:
            await self.bot.send_message(ctx.message.channel, embed=await self.get_case_embed(case))
        except InvalidArgument:
            await self.bot.send_message(ctx.message.channel, "Invalid case number")

    @moderation.group(pass_context=True, no_pm=True, aliases=['purge', 'purgemessages'])
    @checks.have_required_level(3)
    async def remove(self, ctx):  # borrowed from the RDanny code
        """Removes messages that meet a criteria.

        When the command is done doing its work, you will get a private message
        detailing which users got removed and how many messages got removed.
        """

        if ctx.invoked_subcommand is None:
            await self.bot.say('Invalid criteria passed "{0.subcommand_passed}"'.format(ctx))

    async def do_removal(self, message, limit, predicate):
        deleted = await self.bot.purge_from(message.channel, limit=limit, before=message, check=predicate)
        spammers = Counter(m.author.display_name for m in deleted)
        messages = ['%s %s removed.' % (len(deleted), 'message was' if len(deleted) == 1 else 'messages were')]
        if len(deleted):
            messages.append('')
            spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
            messages.extend(map(lambda t: '**{0[0]}**: {0[1]}'.format(t), spammers))

        await self.bot.say('\n'.join(messages), delete_after=10)

    @remove.command(pass_context=True)
    async def embeds(self, ctx, search=100):
        """Removes messages that have embeds in them."""
        await self.do_removal(ctx.message, search, lambda e: len(e.embeds))

    @remove.command(pass_context=True)
    async def files(self, ctx, search=100):
        """Removes messages that have attachments in them."""
        await self.do_removal(ctx.message, search, lambda e: len(e.attachments))

    @remove.command(pass_context=True)
    async def images(self, ctx, search=100):
        """Removes messages that have embeds or attachments."""
        await self.do_removal(ctx.message, search, lambda e: len(e.embeds) or len(e.attachments))

    @remove.command(name='all', pass_context=True)
    async def _remove_all(self, ctx, search=100):
        """Removes all messages."""
        await self.do_removal(ctx.message, search, lambda e: True)

    @remove.command(pass_context=True)
    async def user(self, ctx, member: discord.Member, search=100):
        """Removes all messages by the member."""
        await self.do_removal(ctx.message, search, lambda e: e.author == member)

    @remove.command(pass_context=True)
    async def contains(self, ctx, *, substr: str):
        """Removes all messages containing a substring.
        The substring must be at least 3 characters long.
        """
        if len(substr) < 3:
            await self.bot.say('The substring length must be at least 3 characters.')
            return

        await self.do_removal(ctx.message, 100, lambda e: substr in e.content)

    @remove.command(name='bot', pass_context=True)
    async def _bot(self, ctx, prefix, *, member: discord.Member):
        """Removes a bot user's messages and messages with their prefix.
        The member doesn't have to have the [Bot] tag to qualify for removal.
        """

        def predicate(m):
            return m.author == member or m.content.startswith(prefix)

        await self.do_removal(ctx.message, 100, predicate)

    @remove.command(pass_context=True)
    async def custom(self, ctx, *, args: str):
        """A more advanced prune command.
        Allows you to specify more complex prune commands with multiple
        conditions and search criteria. The criteria are passed in the
        syntax of `--criteria value`. Most criteria support multiple
        values to indicate 'any' match. A flag does not have a value.
        If the value has spaces it must be quoted.
        The messages are only deleted if all criteria are met unless
        the `--or` flag is passed.
        Criteria:
          user      A mention or name of the user to remove.
          contains  A substring to search for in the message.
          starts    A substring to search if the message starts with.
          ends      A substring to search if the message ends with.
          bot       A flag indicating if it's a bot user.
          embeds    A flag indicating if the message has embeds.
          files     A flag indicating if the message has attachments.
          emoji     A flag indicating if the message has custom emoji.
          search    How many messages to search. Default 100. Max 2000.
          or        A flag indicating to use logical OR for all criteria.
          not       A flag indicating to use logical NOT for all criteria.
        """

        class Arguments(argparse.ArgumentParser):
            def error(self, message):
                raise RuntimeError(message)

        parser = Arguments(add_help=False, allow_abbrev=False)
        parser.add_argument('--user', nargs='+')
        parser.add_argument('--contains', nargs='+')
        parser.add_argument('--starts', nargs='+')
        parser.add_argument('--ends', nargs='+')
        parser.add_argument('--or', action='store_true', dest='_or')
        parser.add_argument('--not', action='store_true', dest='_not')
        parser.add_argument('--emoji', action='store_true')
        parser.add_argument('--bot', action='store_const', const=lambda m: m.author.bot)
        parser.add_argument('--embeds', action='store_const', const=lambda m: len(m.embeds))
        parser.add_argument('--files', action='store_const', const=lambda m: len(m.attachments))
        parser.add_argument('--search', type=int, default=100)

        try:
            args = parser.parse_args(shlex.split(args))
        except Exception as e:
            await self.bot.say(str(e))
            return

        predicates = []
        if args.bot:
            predicates.append(args.bot)

        if args.embeds:
            predicates.append(args.embeds)

        if args.files:
            predicates.append(args.files)

        if args.emoji:
            custom_emoji = re.compile(r'<:(\w+):(\d+)>')
            predicates.append(lambda m: custom_emoji.search(m.content))

        if args.user:
            users = []
            for u in args.user:
                try:
                    converter = commands.MemberConverter(ctx, u)
                    users.append(converter.convert())
                except Exception as e:
                    await self.bot.say(str(e))
                    return

            predicates.append(lambda m: m.author in users)

        if args.contains:
            predicates.append(lambda m: any(sub in m.content for sub in args.contains))

        if args.starts:
            predicates.append(lambda m: any(m.content.startswith(s) for s in args.starts))

        if args.ends:
            predicates.append(lambda m: any(m.content.endswith(s) for s in args.ends))

        op = all if not args._or else any

        def predicate(m):
            r = op(p(m) for p in predicates)
            if args._not:
                return not r
            return r

        args.search = max(0, min(2000, args.search))  # clamp from 0-2000
        await self.do_removal(ctx.message, args.search, predicate)


def setup(bot):
    bot.add_cog(Mods(bot))
