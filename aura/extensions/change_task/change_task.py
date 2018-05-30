from discord.ext import commands
from aura.lib import db
from aura.lib import game_functions
from aura.core import checks
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
            await ctx.message.delete()
        sql = ''' SELECT * FROM eve_rpg_players WHERE `player_id` = (?) '''
        values = (ctx.message.author.id,)
        player = await db.select_var(sql, values)
        current_task = await game_functions.get_task(int(player[0][6]))
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Change Task",
                        value="**Current Task** - {}\n\n"
                              "**Dock**\n"
                              "**1.** Dock in current region.\n"
                              "**PVP Tasks**\n"
                              "**2.** Go on a solo PVP roam.\n"
                              "**3.** Camp a gate in your current region.\n"
                              "**4.** Try to gank someone.\n"
                              "**5.** Join a fleet.\n"
                              "**PVE Tasks**\n"
                              "**6.** Kill belt rats.\n"
                              "**7.** Run anomalies in the system.\n"
                              "**8.** Do some exploration and run sites in the system.\n"
                              "**Mining Tasks**\n"
                              "**9.** Go try and kill belt rats.\n"
                              "**10.** Go try and kill belt rats.\n".format(current_task))
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author

        msg = await self.bot.wait_for('message', check=check, timeout=60.0)
        content = msg.content
        if content == '5' or content == '4' or content == '8' or content == '9' or content == '10':
            return await ctx.author.send('**Not Yet Implemented**')
        elif 0 < int(content) < 11:
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
            return await ctx.author.send('**Task Updated** - You are now {}.'.format(new_task))
        else:
            return await ctx.author.send('**ERROR** - Not a valid choice.')