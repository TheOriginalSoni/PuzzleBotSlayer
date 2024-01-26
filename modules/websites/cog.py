import os
import nextcord
import re
import urllib
from nextcord.ext import commands
from utils import discord_utils, logging_utils
from utils.anagram import anagrams
from utils.wordlist import cromulence
from utils import ciphers, external_api, paging_utils
#from utils.registrar import WORD_SET_TESTS
"""
Wesbites module. 
"""

class WebsitesCog(commands.Cog, name="Websites"):
    """
    All random websites
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="nutrimatic", aliases=["n","nu","nut","nutri"])
    async def nutrimatic(self, ctx, *, query=None):
        if not query:
            await ctx.send('Example regex: `!nut "<asympote_>"`')
            return

        query = query.replace("`", "")
        query = query.replace("\\", "")

        query_initial = query[:]
        query = (
            query_initial.replace("&", "%26")
            .replace("+", "%2B")
            .replace("#", "%23")
            .replace(" ", "+")
        )  # html syntax
        url = "https://nutrimatic.org/?q=" + query + "&go=Go"
        text = urllib.request.urlopen(url).read()
        text1 = text.decode()

        # set up embed template
        embed = nextcord.Embed(
            title="Your nutrimatic link", url=url, colour=nextcord.Colour.magenta()
        )
        embed.set_footer(text="Query: " + query_initial)

        # parse for solution list
        posA = [m.start() for m in re.finditer("<span", text1)]
        posB = [m.start() for m in re.finditer("</span", text1)]

        # check for no solutions, send error
        if not posA:
            final = "None"
            errA = [m.start() for m in re.finditer("<b>", text1)]
            errB = [m.start() for m in re.finditer("</b>", text1)]
            final = text1[errA[-1] + 3 : errB[-1]]
            if final.find("font") != -1:
                errA = [m.start() for m in re.finditer("<font", text1)]
                errB = [m.start() for m in re.finditer("</font>", text1)]
                final = text1[errA[-1] + 16 : errB[-1]]
            embed.description = final
            await ctx.send(embed=embed)
            return

        # check for ending error message, usually bolded
        # max number of solutions on a nutrimatic page is 100
        finalend = None
        if len(posA) < 100:
            try:
                errA = [m.start() for m in re.finditer("<b>", text1)]
                errB = [m.start() for m in re.finditer("</b>", text1)]
                finalend = text1[errA[-1] + 3 : errB[-1]]
            except:
                pass

        # prep solution and weights for paginator
        solutions = []
        weights = []
        for n in range(0, min(len(posA), 200)):
            word = text1[posA[n] + 36 : posB[n]]
            size = float(text1[posA[n] + 23 : posA[n] + 32])
            solutions.append(word)
            weights.append(size)

        p = paging_utils.Pages(
            ctx, solutions=solutions, weights=weights, embedTemp=embed, endflag=finalend
        )
        await p.pageLoop()

    @commands.command(name="cromulence", aliases=['crom'])
    async def cromulence(self, ctx, *args):
        """
        Cromulence command. It does #TODO
        """
        await logging_utils.log_command("cromulence", ctx.guild, ctx.channel, ctx.author)
        embed = discord_utils.create_embed()

        content = ''.join(args)
        response = cromulence(content)
        embed.add_field(name="SUCCESS", value=response)
        await ctx.send(embed)


    @commands.command(name="onelook", aliases=['o', 'ol'])
    async def onelook(self, ctx, *tokens):
        """
        Searches your query on onelook. It does #TODO
        """
        await logging_utils.log_command("onelook", ctx.guild, ctx.channel, ctx.author)
        embed = discord_utils.create_embed()

        content = ' '.join(tokens)

        url, results = external_api.onelook(content)
        if len(results) == 0:
            await ctx.send('<' + url + '>\nNothing found')
            return

        await ctx.send('<' + url +
                                '>\n```\n' +
                                '\n'.join(results) + '```')
        return


    @commands.command(aliases=['r'])
    async def regex(self, ctx, *tokens):
        """
        COMMAND DESCRIPTION #TODO
        """
        await logging_utils.log_command("regex", ctx.guild, ctx.channel, ctx.author)
        embed = discord_utils.create_embed()

        if len(tokens) <= 0 or tokens[0].lower() == 'help':
            help_str = '\n'.join(constants.REGEX_HELP_STR)
            await ctx.send(help_str)
            return

        dictionary = 'ukacd'
        dictionary_mappings = {
            'standard': 'standard',
            'small': 'standard',
            'ukacd': 'ukcryptic',
            'cryptic': 'ukcryptic',
            'medium': 'ukcryptic',
            'scrabble': 'ospdlong',
            'oed': 'oed',
            'onelook': 'onelook',
            'large': 'onelook',
            'huge': 'onelook',
            'wikipedia': 'wikititles',
            'cities': 'cities',
            'movies': 'movies',
            'bible': 'bible',
        }
        if tokens[0].lower() in dictionary_mappings.keys():
            dictionary = dictionary_mappings[tokens[0]]
            content = ' '.join(tokens[1:])
        else:
            content = ' '.join(tokens[0:])

        if dictionary == 'onelook':
            content = content.replace(' ', '_').replace('$', ' ')

        url, results = external_api.regex(content, dictionary)
        if len(results) == 0:
            await ctx.send('(via <' + url + '>)\nNothing found')
            return

        results = [r.replace('_', ' ') for r in results]
        results = '\n'.join(results)[:1900]

        await ctx.send('(via <' + url +
                                '>)\n```\n' +
                                results + '```')
        return


    @commands.command(aliases=['c'])
    async def crossword(self, ctx, *tokens):
        """
        COMMAND DESCRIPTION #TODO
        """
        await logging_utils.log_command("crossword", ctx.guild, ctx.channel, ctx.author)
        embed = discord_utils.create_embed()

        def _print_row(row, max_answer_length):
            print(row)
            return ('*' * row[0] + ' ' * (5 - row[0]) + ' ' +
                    row[1].ljust(max_answer_length) + ' ' +
                    row[2])

        content = ' '.join(tokens)

        url, response = external_api.crossword(content)

        max_answer_length = max([len(row[1]) for row in response])
        response_str = '\n'.join(_print_row(row, max_answer_length) for row in response)
        response_str = '<' + url + '>\n```\n' + response_str + '\n```'
        await ctx.send(response_str)


    @commands.command(aliases=['syn', 'syns', 'synonyms'])
    async def synonym(self, ctx, *tokens):
        """
        COMMAND DESCRIPTION #TODO
        """
        await logging_utils.log_command("synonym", ctx.guild, ctx.channel, ctx.author)
        embed = discord_utils.create_embed()
        content = ' '.join(tokens)

        response = external_api.synonyms(content)
        response = '`' + ' '.join(response)[:1350] + '`'
        await ctx.send(response)


    @commands.command(aliases=['ant', 'ants', 'antonyms', 'opps', \
                    'opposite', 'opposites'])
    async def antonym(self, ctx, *tokens):
        """
        COMMAND DESCRIPTION #TODO
        """
        await logging_utils.log_command("antonym", ctx.guild, ctx.channel, ctx.author)
        embed = discord_utils.create_embed()
        content = ' '.join(tokens)

        response = external_api.antonyms(content)
        response = '`' + ' '.join(response)[:1350] + '`'
        await ctx.send(response)

    @commands.command(aliases=['v', 'vignere'])
    async def vigenere(self, ctx, *args):
        """
        COMMAND DESCRIPTION #TODO
        """
        await logging_utils.log_command("vignere", ctx.guild, ctx.channel, ctx.author)
        embed = discord_utils.create_embed()
        tokens = ' '.join(args)
        key, decoded = external_api.solve_vigenere(tokens)
        response = f'{decoded}\n(key: {key})'
        await ctx.send(response)


    @commands.command(aliases=['qq', 'quip', 'quipquip', 'qiupqiup', 'quipqiup', \
                    'crypto'])
    async def cryptogram(self, ctx, *args):
        """
        COMMAND DESCRIPTION #TODO
        """
        await logging_utils.log_command("cryptogram", ctx.guild, ctx.channel, ctx.author)
        embed = discord_utils.create_embed()
        tokens = ' '.join(args)

        responses = external_api.solve_cryptogram(tokens)
        response = '```\n' + '\n'.join(
                [f'({k["logp"]:.2f}) {k["plaintext"]}  | KEY: {k["key"]}'
                for k in responses[:8]]) + '\n```'
        await ctx.send(response)


    @commands.command(aliases=['q'])
    async def qat(self, ctx, *args):
        """
        COMMAND DESCRIPTION #TODO
        """
        await logging_utils.log_command("qat", ctx.guild, ctx.channel, ctx.author)
        embed = discord_utils.create_embed()
        content = ''.join(args)

        url, results = external_api.qat(content)
        url_r = '<' + url + '>\n'
        response = ''
        joiner = ' ' if ';' not in content else '\n'

        for key in results.keys():
            if len(results[key]) == 0:
                continue

            intermed = joiner.join(results[key])
            length_prefix = f'**Length {key}**\n' if key > 0 else ''
            response = response + f'{length_prefix}```\n{intermed}\n```'
        if len(response):
            response = response[:1350]
            backticks = response[-3:].count('`')
            response += '`' * (3 - backticks)
        else:
            response = f'No results {random_nature_emoji()}'
        await ctx.send(url_r + response)


    @commands.command(aliases=['t', 'common'])
    async def commonalities(self, ctx, *args):
        """
        COMMAND DESCRIPTION #TODO
        """
        await logging_utils.log_command("commonalities", ctx.guild, ctx.channel, ctx.author)
        embed = discord_utils.create_embed()
        words = [w.lower() for w in args]

        if len(words) < 3:
            await ctx.send('I need at least 3 words')
            return

        msg = []
        for test_name, test in WORD_SET_TESTS.items():
            passed_tests = test(words)
            if not passed_tests:
                continue
            
            for return_str in passed_tests:
                msg.append(return_str)

        msg = '\n'.join(msg) if len(msg) else 'Sorry, couldn\'t find anything :('
        await ctx.send(msg)


    @commands.command(aliases=['wolfram', 'alpha', 'wa'])
    async def wolframalpha(self, ctx, *args):
        """
        COMMAND DESCRIPTION #TODO
        """
        await logging_utils.log_command("wolframalpha", ctx.guild, ctx.channel, ctx.author)
        embed = discord_utils.create_embed()
        if len(args) > 0:
            words = ' '.join(args)
            out = external_api.wolfram_alpha(words)
            while sum(map(len, out)) > 2000:
                out.pop()
            await ctx.send(''.join(out))


def setup(bot):
    bot.add_cog(WebsitesCog(bot))
