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
        sql = ''' SELECT * FROM eve_rpg_players ORDER BY `kills` DESC LIMIT 10 '''
        top_killers = await db.select(sql)
        top_killers_array = []
        for killers in top_killers:
            top_killer_user = self.bot.get_user(int(killers[2]))
            if top_killer_user is None:
                display_name = 'Unknown'
            else:
                display_name = top_killer_user.display_name
            top_killers_array.append('{} - {} Kills'.format(display_name, killers[10]))
        killers_list = '\n'.join(top_killers_array)
        sql = ''' SELECT * FROM eve_rpg_players ORDER BY `losses` DESC LIMIT 10 '''
        top_losers = await db.select(sql)
        top_losers_array = []
        for losers in top_losers:
            top_losers_user = self.bot.get_user(int(losers[2]))
            if top_losers_user is None:
                display_name = 'Unknown'
            else:
                display_name = top_losers_user.display_name
            top_losers_array.append('{} - {} Losses'.format(display_name, losers[11]))
        losers_list = '\n'.join(top_losers_array)
        sql = ''' SELECT * FROM eve_rpg_players ORDER BY `isk` DESC LIMIT 10 '''
        top_isk = await db.select(sql)
        top_isk_array = []
        for isk in top_isk:
            top_isk_user = self.bot.get_user(int(isk[2]))
            if top_isk_user is None:
                display_name = 'Unknown'
            else:
                display_name = top_isk_user.display_name
            clean_isk = '{0:,.2f}'.format(float(isk[5]))
            top_isk_array.append('{} - {} ISK'.format(display_name, clean_isk))
        isk_list = '\n'.join(top_isk_array)
        sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 2 OR `task` = 3 OR`task` = 4 OR`task` = 5 '''
        pvp_active = await db.select(sql)
        sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 6 OR `task` = 7 OR`task` = 8 '''
        pve_active = await db.select(sql)
        sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 9 OR `task` = 10 '''
        mining_active = await db.select(sql)
        sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 1 OR `task` = 20 OR `task` = 21 '''
        other_active = await db.select(sql)
        embed = make_embed(guild=ctx.guild)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Provided Via Firetail Bot")
        embed.add_field(name="Kills Leaderboard",
                        value=killers_list, inline=False)
        embed.add_field(name="Loss Leaderboard",
                        value=losers_list, inline=False)
        embed.add_field(name="Richest Players",
                        value=isk_list, inline=False)
        embed.add_field(name="Player Counts",
                        value='{} - Actively PVPing\n{} - Actively PVEing\n{} - Actively Mining\n{} - Docked/In-Space/'
                              'Traveling'.format(
                            len(pvp_active), len(pve_active), len(mining_active), len(other_active)
                        ), inline=False)
        await ctx.channel.send(embed=embed)
