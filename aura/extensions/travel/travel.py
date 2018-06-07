from discord.ext import commands

from aura.core import checks
from aura.lib import db
from aura.lib import game_functions
from aura.utils import make_embed


class Travel:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session
        self.config = bot.config
        self.logger = bot.logger

    @commands.command(name='travel', case_insensitive=True)
    @checks.spam_check()
    @checks.is_whitelist()
    @checks.has_account()
    async def travel(self, ctx):
        """Travel to a new region."""
        if ctx.guild is not None:
            try:
                await ctx.message.delete()
            except Exception:
                pass
        sql = ''' SELECT * FROM eve_rpg_players WHERE `player_id` = (?) '''
        values = (ctx.message.author.id,)
        player = await db.select_var(sql, values)
        region_id = int(player[0][4])
        region_name = await game_functions.get_region(region_id)
        connected_regions = []
        connected_regions_detail = {}
        options = []
        option_number = 1
        region_connections = await game_functions.get_region_connections(region_id)
        for regions in region_connections:
            name = await game_functions.get_region(regions)
            sec = await  game_functions.get_region_security(regions)
            connected_regions_detail[option_number] = regions
            options.append(option_number)
            connected_regions.append('**{}.** {} ({} Sec)'.format(option_number, name, sec))
            option_number += 1
        region_list = '\n'.join(connected_regions)
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Travel",
                        value="**Current Region** - {}\n\n{}".format(region_name, region_list))
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120.0)
        content = msg.content
        if int(content) in options:
            sql = ''' UPDATE eve_rpg_players
                    SET destination = (?),
                        task = 20
                    WHERE
                        player_id = (?); '''
            target = connected_regions_detail[int(content)]
            values = (int(target), ctx.author.id,)
            destination = await game_functions.get_region(int(content))
            await db.execute_sql(sql, values)
            await ctx.author.send('**Task Updated** - You are now traveling to {}.'.format(destination))
        elif content == '5':
            await ctx.author.send('**Not Yet Implemented**')
        else:
            await ctx.author.send('**ERROR** - Not a valid choice.')
        return await ctx.invoke(self.bot.get_command("me"), True)
