import os
from nextcord.ext import commands
from utils import discord_utils, logging_utils
from utils.anagram import anagrams
"""
Anagrams module.
"""

class AnagramsCog(commands.Cog, name="Anagrams"):
    """
    Anagrams code
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="anagram")
    async def anagram(self, ctx, text:str):
        """Anagrams all words

        Usage : `~anagram "word"`
        """
        await logging_utils.log_command("anagram", ctx.guild, ctx.channel, ctx.author)
        embed = discord_utils.create_embed()

        if(len(text)<=0):
            embed.add_field(
                name="ERROR: No text given",
                value=f"Text cannot be empty. Please give text to anagram",
                inline=False,
            )
            await ctx.send(embed=embed)
            return

        #def anagrams(text, wildcards=0, wordlist=WORDS, count=100, quiet=False, time_limit=None):
        results  = anagrams(text)
        message = "\n".join(results)

        embed.add_field(
            name=f"Anagrams of {text}",
            value=f"{message}",
            inline=False,
        )
        embeds = discord_utils.split_embed(embed)
        for emb in embeds:
            await ctx.send(embed=emb)


def setup(bot):
    bot.add_cog(AnagramsCog(bot))
