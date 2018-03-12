import logging

from discord.ext import commands


class CustomContext(commands.Context):

    def __init__(self, **attrs):
        super().__init__(**attrs)

    @property
    def logger(self):
        # Copy that to log
        extra = {"channelid" : self.channel.id, "userid": self.author.id}
        logger = logging.LoggerAdapter(self.bot.base_logger, extra)
        return logger



