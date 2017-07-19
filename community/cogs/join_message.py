# -*- coding: utf-8 -*-
# !/usr/bin/env python3.5

"""

"""


class WelcomeMessage:
    def __init__(self, bot):
        self.bot = bot
        self.message = """Hello and welcome to the DuckHunt server.
I know welcome messages can be annoying for you, but if you read this one, you will most likely find an answer.

**FAQ** :

You can access the most frequently asked questions (How to setup the bot, how to play...) using the *Community Bot*, type `c!faq` to get started!
If you need, here is the website link: https://api-d.com

**Support**:

If you need some help with the bot, please ask on #support_english *(ou #support_francais si vous êtes francais :p)*, and **WAIT** (and by wait I mean don't leave) for an answer. We sometimes sleep, you can receive an admin response in less than 12 hours, but it's less usually. :)

**If you have duckhunt installed on your server**:

Please ask an admin for the Server Owner rank.

**Rules** :

1/ Use your mind. Thanks.
2/ Moderators are always right"""

    async def on_member_join(self, member):
        await self.bot.send_message(member, self.message)


def setup(bot):
    bot.add_cog(WelcomeMessage(bot))
