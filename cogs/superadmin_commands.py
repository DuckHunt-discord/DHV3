import asyncio
import collections
import inspect

import discord

from cogs import spawning
from discord.ext import commands
from cogs.helpers import checks
import random


class SuperAdmin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.is_super_admin()
    async def webinterface_roles(self, ctx):
        roles = {
            '$admins'                        : 'Owner',
            '$moderators'                    : 'Moderator',
            '$translators'                   : 'Translator',
            '$bug_hunters'                   : 'Bug Hunters',
            '$proficients'                   : 'Proficient',
            '$partners'                      : 'Partner',
            '$donators'                      : 'Donator',
            '$enigma_event_winners_june_2018': 'DuckEnigma Event Winner 2018',
            '$enigma_event_winners_november_2019': 'Eminigma Event Winner 2019'

        }

        member_list = sorted(ctx.guild.members, key=lambda u: u.name)

        for role_var in sorted(roles.keys()):
            role_name = roles[role_var]

            role = discord.utils.get(ctx.guild.roles, name=role_name)
            php_code = '```'
            php_code += f"{role_var} = array(\n"

            for member in member_list:
                if role in member.roles:
                    php_code += f"{member.id}, // {member.name}#{member.discriminator}\n"

            php_code += ");\n\n"

            php_code += '```'

            await ctx.send(php_code, delete_after=120)

    @commands.command()
    @checks.is_super_admin()
    async def get_level_from_exp(self, ctx, exp: int):
        await self.bot.send_message(ctx=ctx, message=await self.bot.db.get_level(exp))

    @commands.command()
    @checks.is_super_admin()
    async def leave_everywhere(self, ctx):
        for guild in self.bot.guilds:
            if guild != ctx.guild:
                # Dangerous command
                # await guild.leave()
                ctx.logger.info(f"I would leave {guild.id}/{guild.name}")

        await self.bot.send_message(ctx=ctx, message="Check console")

    @commands.command(aliases=["gen_event", "event_gen"])
    @checks.is_super_admin()
    async def regen_event(self, ctx, force: bool = True):
        """!regen_event"""
        await spawning.event_gen(ctx.bot, force)
        await self.bot.send_message(ctx=ctx, message=":ok_hand: Next event regenerated")

    @commands.command(aliases=["quit", "stop"])
    @checks.is_super_admin()
    async def exit(self, ctx):
        """Quit the bot, duh"""
        await self.bot.log(level=40, title="Bot is restarting", message=f"Exited with command", where=ctx)
        await self.bot.send_message(ctx=ctx, message="Restarting... This may take a while.")
        raise KeyboardInterrupt("Exited with command")

    @commands.command()
    @checks.is_super_admin()
    async def reload_translations(self, ctx):
        """Reload the bot translations"""
        await self.bot.log(level=1, title="Reloading bot translations", message=f"Translations are being reloaded",
                           where=ctx)
        if self.bot.translations.reload():
            await self.bot.send_message(ctx=ctx, message=":ok_hand: Translations reloaded")
        else:
            await self.bot.send_message(ctx=ctx, message=":x: Error reloading translations :(")

    @commands.command()
    @checks.is_super_admin()
    async def find_same_discrim(self, ctx, current_discriminator:str=None, wanted_discriminator:str="0001"):
        """Find names with a discriminator used"""

        await ctx.send(f"We'll get you the #{wanted_discriminator}, please wait a moment for me to search for candidates...")

        big_dict_of_names_and_discrims = collections.defaultdict(set)
        set_of_intresting_names = set()
        for user in self.bot.users:
            name = user.name
            discrim = user.discriminator
            if discrim is None:
                break

            if current_discriminator is None or discrim == current_discriminator:
                set_of_intresting_names.add(name)

            big_dict_of_names_and_discrims[name].add(discrim)

        # await ctx.send(f"I found some names with the same discriminator as you: {set_of_intresting_names}")

        unintresting_names = set()
        intresting_names_dict = {}
        for name in set_of_intresting_names:
            if wanted_discriminator in big_dict_of_names_and_discrims[name]:
                unintresting_names.add(name)
            else:
                intresting_names_dict[name] = len(big_dict_of_names_and_discrims[name])

        sorted_intresting = sorted(intresting_names_dict.items(), key=lambda kv: -kv[1])

        if len(unintresting_names) > 0:
            await ctx.send(f"You shouldn't try to change to one of these: {unintresting_names}, as the #{wanted_discriminator} is already taken :("[:1900])

        await ctx.send(f"The **best names** to try would be, in order of preference, {sorted_intresting[:10]}")

        for i in range(min(3, len(sorted_intresting))):
            name, nd = sorted_intresting[i]
            await ctx.send(f"`{name}` taken discrims: {big_dict_of_names_and_discrims[name]}"[:1900])

    @commands.command()
    @checks.is_super_admin()
    async def server_owners_manager(self, ctx):

        guild = self.bot.get_guild(195260081036591104)

        guild_members = {m.id: m for m in guild.members}

        guild_members_ids = set(guild_members.keys())

        for role in guild.roles:
            if role.id == 241997218276573184:
                so_role = role
                people_with_role = role.members
                break
        else:
            await self.bot.send_message(ctx=ctx, message=f"Role not found")
            return

        await self.bot.send_message(ctx=ctx, message=f"Got server owner role.")

        admins_ids = set(await self.bot.db.get_all_admins_ids())

        await self.bot.send_message(ctx=ctx, message=f"Got {len(admins_ids)} from the db.")

        active_guilds = {channel.guild for channel in self.bot.ducks_planning.keys()}

        for guild in self.bot.guilds:
            if guild not in active_guilds:
                continue

            for member in guild.members:
                if member.guild_permissions.administrator and not member.bot:
                    admins_ids.add(member.id)

        await self.bot.send_message(ctx=ctx, message=f"{len(admins_ids)} servers owners in total the bot can see.")

        people_with_role_ids = set([m.id for m in people_with_role])

        people_that_shouldnt_have_the_role = people_with_role_ids.difference(admins_ids)

        people_that_should_have_the_role_but_dont = (guild_members_ids - people_with_role_ids).intersection(admins_ids)

        await self.bot.send_message(ctx=ctx, message=f"{len(people_with_role_ids)} total people have the role. "
                                                     f"{len(people_that_shouldnt_have_the_role)} people shouldn't. "
                                                     f"However, {len(people_that_should_have_the_role_but_dont)} should have the role but dont.")

        await self.bot.send_message(ctx=ctx, message=f"Shouldn't: {[guild_members[mid].name for mid in random.sample(people_that_shouldnt_have_the_role, min(20, len(people_that_shouldnt_have_the_role)))]}")
        await self.bot.send_message(ctx=ctx, message=f"Should: {[guild_members[mid].name for mid in random.sample(people_that_should_have_the_role_but_dont, min(20, len(people_that_should_have_the_role_but_dont)))]}")

        def remove_so_role(roles):
            rl = list(roles)
            rl.remove(so_role)
            return rl

        with open("server_owner_manager.txt", "w") as f:
            f.write("Removed the Server Owner role from these people: \n")
            for member_id in people_that_shouldnt_have_the_role:
                member = guild_members[member_id]
                try:
                    await member.edit(roles=remove_so_role(member.roles), reason="server_owners_manager")
                except discord.HTTPException as e:
                    f.write(f"\to {member.name}#{member.discriminator} ({member_id}) -- {e.text}\n")
                else:
                    f.write(f"\t* {member.name}#{member.discriminator} ({member_id})\n")

            await self.bot.send_message(ctx=ctx, message=f"Finished the small part of removing the role, now we are on for a bigger wait...")

            f.write("\n\nAdded the Server Owner role to these people: \n")
            for member_id in people_that_should_have_the_role_but_dont:
                member = guild_members[member_id]
                try:
                    await member.edit(roles=list(member.roles) + [so_role], reason="server_owners_manager")
                except discord.HTTPException as e:
                    print("ko " + e.text)
                    f.write(f"\to {member.name}#{member.discriminator} ({member_id}) -- {e.text}\n")
                else:
                    print("ok")
                    f.write(f"\t* {member.name}#{member.discriminator} ({member_id})\n")

        with open("server_owner_manager.txt", "rb") as f:
            await ctx.send(content="Done.", file=discord.File(fp=f, filename="server_owners.txt"))


def setup(bot):
    bot.add_cog(SuperAdmin(bot))
