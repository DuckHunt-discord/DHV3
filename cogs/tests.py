# Minimal Working Example for invoke orders when using command groups
# Result : https://api-d.com/snaps/2018-02-13_18-58-06-s1js07i301.png
from discord.ext import commands


class Tests:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def command(self, ctx):
        for server_id in ["212323451707326465", "226754022797737992", "270626317672644609", "285394353109860352", "299964195728785408",
          "306963164308963329", "318432417625014272", "320799038242947083", "330052262779158529", "341651392336887808",
          "346464171896078336", "360651251706494987", "368208867206889486", "369616761206865931", "387081943419846656",
          "391661947654897665", "393725813067087873", "411745788847194114"]:
            server_id = int(server_id)
            server = self.bot.get_guild(server_id)

            if server:

                for channel in server.channels:
                    try:
                        await ctx.send(await channel.create_invite(reason="Warning global_scores",max_uses=1))
                        break
                    except:
                        pass



def setup(bot):
    bot.add_cog(Tests(bot))
