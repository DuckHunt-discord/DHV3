import asyncio
import inspect

import discord

from cogs import spawning
from discord.ext import commands
from cogs.helpers import checks
import random


class SuperAdmin:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.is_super_admin()
    @checks.is_channel_enabled()
    async def db_id(self, ctx):
        dbid = await self.bot.db.get_channel_dbid(ctx.channel)
        await self.bot.send_message(ctx=ctx, message=f"Channel ID in the DB is {dbid}")

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

    @commands.command(pass_context=True)
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
                    print("ko " + e.text)
                    f.write(f"\to {member.name}#{member.discriminator} ({member_id}) -- {e.text}\n")
                else:
                    print("ok")
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


    @commands.command(pass_context=True)
    @checks.is_super_admin()
    async def broadcast(self, ctx, *, bc: str):
        """!broadcast [message]"""
        await self.bot.send_message(ctx=ctx, message="Starting the broadcast...")
        ctx.logger.warning(f"Starting broadcast with message : \n{bc}")
        channels = list(self.bot.ducks_planning.keys())
        total = len(channels)
        i = 0
        f = 0
        for channel in channels:
            i += 1
            if channel.guild.id in [268479971410837504, 336642139381301249]:
                continue
            try:
                await channel.send(content=bc.format(channel_id=channel.id))
                ctx.logger.debug(f"Broadcast : {i}/{total}")
                await asyncio.sleep(3)
                if i % 50 == 0:
                    await self.bot.send_message(ctx=ctx, message=f"{i}/{total} ({f} failed)")
            except Exception as e:
                f += 1
                ctx.logger.info(f"Error broadcasting to {channel.name} : {e}")
                pass

        ctx.logger.info("Broadcast done.")
        await self.bot.send_message(ctx=ctx, message="Broadcast finished!", return_message=True)  # Rate limits


def setup(bot):
    bot.add_cog(SuperAdmin(bot))
