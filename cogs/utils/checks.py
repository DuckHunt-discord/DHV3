import discord.utils
from discord.ext import commands

from cogs.utils import comm, prefs, scores
from cogs.utils.commons import bot


def is_owner_check(message):
    owner = message.author.id in ['138751484517941259']
    bot.loop.create_task(comm.logwithinfos_message(message, "Check owner : " + str(owner)))
    return owner  # Owner of the bot


def is_banned_check(message):
    banned = scores.getStat(message.channel, message.author, "banned", default=False)
    bot.loop.create_task(comm.logwithinfos_message(message, "Check not banned : " + str(not banned)))
    return banned  # Inverse d'un banissement


def is_admin_check(message):
    admin = message.author.id in prefs.getPref(message.server, "admins")
    bot.loop.create_task(comm.logwithinfos_message(message, "Check admin : " + str(admin)))

    return admin  # Dans la liste des admins d'un serveur (fichier json)


def is_activated_check(message):
    servers = prefs.JSONloadFromDisk("channels.json")
    try:
        if message.channel.id in servers[message.server.id]["channels"]:
            activated = True
        else:
            activated = False
    except KeyError:
        activated = False

    bot.loop.create_task(comm.logwithinfos_message(message, "Check activated here : " + str(activated)))
    return activated

def is_owner():
    return commands.check(lambda ctx: is_owner_check(ctx.message))


def is_not_banned():
    return commands.check(lambda ctx: is_banned_check(ctx.message) and not is_admin_check(ctx.message) and not is_owner_check(ctx.message))


def is_admin():
    return commands.check(lambda ctx: is_owner_check(ctx.message) or is_admin_check(ctx.message))


def is_activated_here():
    return commands.check(lambda ctx: is_activated_check(ctx.message))


# The permission system of the bot is based on a "just works" basis
# You have permissions and the bot has permissions. If you meet the permissions
# required to execute the command (and the bot does as well) then it goes through
# and you can execute the command.
# If these checks fail, then there are two fallbacks.
# A role with the name of Bot Mod and a role with the name of Bot Admin.
# Having these roles provides you access to certain commands without actually having
# the permissions required for them.
# Of course, the owner will always be able to execute commands.

def check_permissions(ctx, perms):
    msg = ctx.message
    if is_owner_check(msg):
        return True

    ch = msg.channel
    author = msg.author
    resolved = ch.permissions_for(author)
    return all(getattr(resolved, name, None) == value for name, value in perms.items())


def role_or_permissions(ctx, check, **perms):
    if check_permissions(ctx, perms):
        return True

    ch = ctx.message.channel
    author = ctx.message.author
    if ch.is_private:
        return False  # can't have roles in PMs

    role = discord.utils.find(check, author.roles)
    return role is not None


def admin_or_permissions(**perms):
    def predicate(ctx):
        return role_or_permissions(ctx, lambda r: r.name == 'Bot Admin', **perms)

    return commands.check(predicate)


def is_in_servers(*server_ids):
    def predicate(ctx):
        server = ctx.message.server
        if server is None:
            return False
        return server.id in server_ids

    return commands.check(predicate)
