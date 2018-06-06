import ast

from discord.ext import commands

from aura.core import checks
from aura.lib import db
from aura.utils import make_embed


class Wallet:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session
        self.config = bot.config
        self.logger = bot.logger

    @commands.command(name='wallet', case_insensitive=True)
    @checks.spam_check()
    @checks.is_whitelist()
    @checks.has_account()
    async def wallet(self, ctx):
        """View your wallet."""
        if ctx.guild is not None:
            try:
                await ctx.message.delete()
            except Exception:
                pass
        sql = ''' SELECT * FROM eve_rpg_players WHERE `player_id` = (?) '''
        values = (ctx.message.author.id,)
        player = await db.select_var(sql, values)
        wallet_balance = '{0:,.2f}'.format(float(player[0][5]))
        if player[0][20] is None:
            embed = make_embed(icon=ctx.bot.user.avatar)
            embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                             text="Aura - EVE Text RPG")
            embed.add_field(name="Wallet",
                            value='__Current ISK:__ {}'.format(wallet_balance))
            await ctx.author.send(embed=embed)
        else:
            wallet_journal = ast.literal_eval(player[0][20])
            journal_array = []
            for entry in wallet_journal:
                journal_isk = '{0:,.2f}'.format(float(entry['isk']))
                journal_array.append("*{}* - {} ISK".format(entry['type'], journal_isk))
            journal_text = '\n'.join(journal_array)
            embed = make_embed(icon=ctx.bot.user.avatar)
            embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                             text="Aura - EVE Text RPG")
            embed.add_field(name="Wallet",
                            value='__Current ISK:__ {}'.format(wallet_balance))
            embed.add_field(name="Transactions",
                            value='__**Type**__ - __**Amount**__\n{}'.format(journal_text))
            await ctx.author.send(embed=embed)
        return await ctx.invoke(self.bot.get_command("me"), True)
