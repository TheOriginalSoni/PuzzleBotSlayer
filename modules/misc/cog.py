import os
from nextcord.ext import commands
from utils import discord_utils, logging_utils
"""
Misc module. A collection of Misc useful/fun commands. Also everything not in any other module.
"""

class MiscCog(commands.Cog, name="Misc"):
    """
    A collection of Misc useful/fun commands.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="about", aliases=["aboutthebot", "github"])
    async def about(self, ctx):
        """A quick primer about BBH and what it does

        Usage : `~about`
        """
        await logging_utils.log_command("about", ctx.guild, ctx.channel, ctx.author)
        embed = discord_utils.create_embed()

        owner = await self.bot.fetch_user(os.getenv("BOT_OWNER_DISCORD_ID"))

        embed.add_field(
            name=f"About Me!",
            value=f"Hello!\n"
            f"Bot Be Hyper is a discord bot that we use while solving Puzzle Hunts.\n"
            f"Any problems? Let {owner.mention} know.",
            inline=False,
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(MiscCog(bot))
