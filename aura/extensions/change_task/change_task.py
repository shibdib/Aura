import ast

from discord.ext import commands

from aura.core import checks
from aura.lib import db
from aura.lib import game_functions
from aura.utils import make_embed


class ChangeTask:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session
        self.config = bot.config
        self.logger = bot.logger

    @commands.command(name='task', case_insensitive=True)
    @checks.spam_check()
    @checks.is_whitelist()
    @checks.has_account()
    async def change_task(self, ctx):
        """Change your current task."""
        if ctx.guild is not None:
            try:
                await ctx.message.delete()
            except Exception:
                pass
        sql = ''' SELECT * FROM eve_rpg_players WHERE `player_id` = (?) '''
        values = (ctx.message.author.id,)
        player = await db.select_var(sql, values)
        if player[0][6] == 20:
            await ctx.author.send('**ERROR** - You need to finish traveling first.')
            return await ctx.invoke(self.bot.get_command("me"), True)
        region_id = int(player[0][4])
        region_security = await game_functions.get_region_security(region_id)
        current_task = await game_functions.get_task(int(player[0][6]))
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        if player[0][22] is not None:
            mission_details = ast.literal_eval(player[0][22])
            mission_task = 'Request a Mission.'
        else:
            mission_task = 'Request a Mission.'
        if region_security != 'High':
            embed.add_field(name="Change Task",
                            value="**Current Task** - {}\n\n"
                                  "**Dock**\n"
                                  "**1.** Dock in current region.\n"
                                  "**PVP Tasks**\n"
                                  "**2.** Go on a solo PVP roam.\n"
                                  "**3.** Camp a gate in your current region.\n"
                                  "**5.** Join a fleet.\n"
                                  "**PVE Tasks**\n"
                                  "**6.** Kill belt rats.\n"
                                  "**7.** Run anomalies in the system.\n"
                                  "**8.** Do some exploration and run sites in the system.\n"
                                  "**9.** {}.\n"
                                  "**Mining Tasks**\n"
                                  "**10.** Mine an asteroid belt.\n"
                                  "**11.** Mine a mining anomaly.\n".format(current_task, mission_task))
            accepted = [1, 2, 3, 5, 6, 7, 8, 9, 10]
        else:
            embed.add_field(name="Change Task",
                            value="**Current Task** - {}\n\n"
                                  "**Dock**\n"
                                  "**1.** Dock in current region.\n"
                                  "**PVP Tasks**\n"
                                  "**4.** Try to gank someone.\n"
                                  "**PVE Tasks**\n"
                                  "**6.** Kill belt rats.\n"
                                  "**8.** Do some exploration and run sites in the system.\n"
                                  "**9.** {}.\n"
                                  "**Mining Tasks**\n"
                                  "**10.** Mine an asteroid belt.\n".format(current_task, mission_task))
            accepted = [1, 4, 6, 8, 9]
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120.0)
        content = msg.content
        if content == '5' or content == '8' or content == '9' or content == '11':
            await ctx.author.send('**Not Yet Implemented**')
        elif int(content) in accepted:
            sql = ''' UPDATE eve_rpg_players
                    SET task = (?)
                    WHERE
                        player_id = (?); '''
            values = (int(content), ctx.author.id,)
            await db.execute_sql(sql, values)
            sql = ''' SELECT * FROM eve_rpg_players WHERE `player_id` = (?) '''
            values = (ctx.message.author.id,)
            player = await db.select_var(sql, values)
            new_task = await game_functions.get_task(int(player[0][6]))
            await ctx.author.send('**Task Updated** - You are now {}.'.format(new_task))
        else:
            await ctx.author.send('**ERROR** - Not a valid choice.')
        return await ctx.invoke(self.bot.get_command("me"), True)
