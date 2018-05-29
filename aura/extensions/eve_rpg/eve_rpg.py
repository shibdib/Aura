from discord.ext import commands
from aura.lib import db
from aura.lib import game_functions
from aura.core import checks
from aura.utils import make_embed
import asyncio
import random


class EveRpg:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session
        self.config = bot.config
        self.logger = bot.logger
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.tick_loop())

    @commands.command(name='rpgStats', aliases=["rpgstats"])
    @checks.spam_check()
    @checks.is_whitelist()
    async def _rpg_stats(self, ctx):
        """Get your RPG Stats"""
        sql = ''' SELECT * FROM eve_rpg_players WHERE `player_id` = (?) '''
        values = (ctx.message.author.id,)
        result = await db.select_var(sql, values)
        sql = ''' SELECT * FROM eve_rpg_players ORDER BY `level` DESC LIMIT 1 '''
        top_level = await db.select(sql)
        top_level_user = self.bot.get_user(int(top_level[0][2]))
        sql = ''' SELECT * FROM eve_rpg_players ORDER BY `kills` DESC LIMIT 1 '''
        top_killer = await db.select(sql)
        top_killer_user = self.bot.get_user(int(top_killer[0][2]))
        if result is None:
            return await ctx.author.send('**Error** - No player found.')
        else:
            ship_attack, ship_defense, ship_maneuverability, ship_tracking = await self.ship_attributes(result)
            item_attack, item_defense, item_maneuverability, item_tracking = await self.item_attributes(result)
            ship_stats = ' {}/{}/{}/{}'.format(ship_attack, ship_defense, ship_maneuverability, ship_tracking)
            item_stats = ' {}/{}/{}/{}'.format(item_attack, item_defense, item_maneuverability, item_tracking)
            embed = make_embed(guild=ctx.guild)
            embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                             text="Provided Via Firetail Bot")
            embed.add_field(name="Stats",
                            value='\n Level: {}\nXP: {}/100\nShip : {}\nAttack/Defense/Maneuverability/Tracking: {}\n'
                                  'Items: {}\nItem Bonuses (Already applied to ship): {}\nKills: {}\nLosses: {}'.format(
                                result[0][5], result[0][6], result[0][7], ship_stats, result[0][8], item_stats,
                                result[0][3], result[0][4]))
            embed.add_field(name="Top Players", value='\n Top Level: {} (Level {})\nMost Kills: {} ({} Kills)'.format(
                top_level_user.display_name, top_level[0][5], top_killer_user.display_name, top_killer[0][3]),
                            inline=False)
            await ctx.channel.send(embed=embed)

    @commands.command(name='rpgTop', aliases=["rpgtop"])
    @checks.spam_check()
    @checks.is_whitelist()
    async def _rpg_top(self, ctx):
        """Get the top RPG players"""
        sql = ''' SELECT * FROM eve_rpg_players WHERE `player_id` = (?) '''
        values = (ctx.message.author.id,)
        result = await db.select_var(sql, values)
        sql = ''' SELECT * FROM eve_rpg_players ORDER BY `level` DESC LIMIT 10 '''
        top_levels = await db.select(sql)
        top_levels_array = []
        for levels in top_levels:
            top_levels_user = self.bot.get_user(int(levels[2]))
            top_levels_array.append('{} - Level {}'.format(top_levels_user.display_name, levels[5]))
        levels_list = '\n'.join(top_levels_array)
        sql = ''' SELECT * FROM eve_rpg_players ORDER BY `kills` DESC LIMIT 10 '''
        top_killers = await db.select(sql)
        top_killers_array = []
        for killers in top_killers:
            top_killer_user = self.bot.get_user(int(killers[2]))
            top_killers_array.append('{} - {} Kills'.format(top_killer_user.display_name, killers[3]))
        killers_list = '\n'.join(top_killers_array)
        if result is None:
            return await ctx.author.send('**Error** - No player found. You must be part of the game to view this')
        else:
            embed = make_embed(guild=ctx.guild)
            embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                             text="Provided Via Firetail Bot")
            embed.add_field(name="Level Leaderboard",
                            value=levels_list, inline=False)
            embed.add_field(name="Kills Leaderboard",
                            value=killers_list, inline=False)
            await ctx.channel.send(embed=embed)

    async def tick_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                await self.process_travel()
                await asyncio.sleep(12)
            except Exception:
                self.logger.exception('ERROR:')
                await asyncio.sleep(5)

    async def process_travel(self):
        sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 20 '''
        travelers = await db.select(sql)
        if travelers is None or len(travelers) is 0:
            return
        for traveler in travelers:
            region_id = int(traveler[4])
            region_security = await game_functions.get_region_security(region_id)
            destination_id = int(traveler[17])
            destination_security = await game_functions.get_region_security(destination_id)
            sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 3 AND `region` = (?) '''
            values = (region_id,)
            outbound_campers = await db.select_var(sql, values)
            sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 3 AND `region` = (?) '''
            values = (destination_id,)
            inbound_campers = await db.select_var(sql, values)
            if len(outbound_campers) is not 0 and region_security != 'High':
                return
            if len(inbound_campers) is not 0 and destination_security != 'High':
                return
            sql = ''' UPDATE eve_rpg_players
                    SET region = (?),
                        task = 21
                    WHERE
                        player_id = (?); '''
            values = (int(destination_id), traveler[2],)
            await db.execute_sql(sql, values)
            player = self.bot.get_user(traveler[2])
            return await player.send('Destination Reached')


    async def weighted_choice(self, items):
        """items is a list of tuples in the form (item, weight)"""
        weight_total = sum((item[1] for item in items))
        n = random.uniform(0, weight_total)
        for item, weight in items:
            if n < weight:
                return item
            n = n - weight
        return item
