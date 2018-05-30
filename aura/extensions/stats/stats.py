from discord.ext import commands

from aura.core import checks
from aura.lib import db
from aura.utils import make_embed


class Stats:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session
        self.config = bot.config
        self.logger = bot.logger

    @commands.command(name='stats', case_insensitive=True)
    @checks.spam_check()
    @checks.is_whitelist()
    async def _rpg_top(self, ctx):
        """Get the top RPG players"""
        sql = ''' SELECT * FROM eve_rpg_players ORDER BY `level` DESC LIMIT 10 '''
        top_levels = await db.select(sql)
        top_levels_array = []
        for levels in top_levels:
            top_levels_user = self.bot.get_user(int(levels[2]))
            top_levels_array.append('{} - Level {}'.format(top_levels_user.display_name, levels[8]))
        levels_list = '\n'.join(top_levels_array)
        sql = ''' SELECT * FROM eve_rpg_players ORDER BY `kills` DESC LIMIT 10 '''
        top_killers = await db.select(sql)
        top_killers_array = []
        for killers in top_killers:
            top_killer_user = self.bot.get_user(int(killers[2]))
            top_killers_array.append('{} - {} Kills'.format(top_killer_user.display_name, killers[10]))
        killers_list = '\n'.join(top_killers_array)
        sql = ''' SELECT * FROM eve_rpg_players ORDER BY `kills` DESC LIMIT 10 '''
        top_losers = await db.select(sql)
        top_losers_array = []
        for losers in top_losers:
            top_losers_user = self.bot.get_user(int(losers[2]))
            top_losers_array.append('{} - {} Kills'.format(top_losers_user.display_name, losers[11]))
        losers_list = '\n'.join(top_losers_array)
        sql = ''' SELECT * FROM eve_rpg_players ORDER BY `isk` DESC LIMIT 10 '''
        top_isk = await db.select(sql)
        top_isk_array = []
        for isk in top_isk:
            top_isk_user = self.bot.get_user(int(isk[2]))
            clean_isk = '{0:,.2f}'.format(float(isk[5]))
            top_isk_array.append('{} - {} ISK'.format(top_isk_user.display_name, clean_isk))
        isk_list = '\n'.join(top_isk_array)
        embed = make_embed(guild=ctx.guild)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Provided Via Firetail Bot")
        embed.add_field(name="Level Leaderboard",
                        value=levels_list, inline=False)
        embed.add_field(name="Kills Leaderboard",
                        value=killers_list, inline=False)
        embed.add_field(name="Loss Leaderboard",
                        value=losers_list, inline=False)
        embed.add_field(name="Richest Players",
                        value=isk_list, inline=False)
        await ctx.channel.send(embed=embed)
