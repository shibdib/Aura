from discord.ext import commands
from aura.lib import db
from aura.lib import game_functions
from aura.core import checks
from aura.utils import make_embed


class ManageSelf:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session
        self.config = bot.config
        self.logger = bot.logger

    @commands.command(name='me')
    @checks.spam_check()
    @checks.is_whitelist()
    @checks.has_account()
    async def _me(self, ctx):
        """Manage your character."""
        sql = ''' SELECT * FROM eve_rpg_players WHERE `player_id` = (?) '''
        values = (ctx.message.author.id,)
        player = await db.select_var(sql, values)
        player_name = self.bot.get_user(int(player[0][2]))
        region_name = await game_functions.get_region(int(player[0][4]))
        current_task = await game_functions.get_task(int(player[0][6]))
        current_ship = player[0][14]
        wallet_balance = player[0][5]
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Welcome {}".format(player_name),
                        value="**Current Region** - {}\n**Current Ship** - {}\n**Current Task** - {}\n"
                              "**Wallet Balance** - {}\n\n"
                              "*User interface initiated.... Select desired action below......*\n\n"
                              "**1.** Change task.\n"
                              "**2.** Travel to a new region.\n"
                              "**3.** Modify current ship.\n"
                              "**4.** Change into another ship.\n"
                              "**5.** Visit the regional market.\n".format(
                            region_name, current_ship, current_task, wallet_balance))
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author

        msg = await self.bot.wait_for('message', check=check, timeout=60.0)
        content = msg.content
        if content == '1':
            await self.change_task(ctx, current_task)
        elif content == '2':
            await self.travel(ctx)
        elif content == '3':
            await self.modify_ship(ctx)
        elif content == '4':
            await self.change_ship(ctx)
        elif content == '5':
            await self.visit_market(ctx)
        else:
            return await ctx.author.send('**ERROR** - Not a valid choice.')

    async def change_task(self, ctx, current_task):
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
                              "**6.** Go try and kill belt rats.\n"
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
        if content == '1' or content == '2' or content == '3' or content == '4' or content == '6' \
                or content == '7' or content == '8' or content == '9' or content == '10':
            sql = ''' UPDATE eve_rpg_players
                    SET task = (?),
                    WHERE
                        player_id = (?); '''
            values = (int(content), ctx.author.id,)
            await db.execute_sql(sql, values)
            sql = ''' SELECT * FROM eve_rpg_players WHERE `player_id` = (?) '''
            values = (ctx.message.author.id,)
            player = await db.select_var(sql, values)
            new_task = await game_functions.get_task(int(player[0][6]))
            return await ctx.author.send('**Task Updated** - You are now {}.'.format(new_task))
        elif content == '5':
            return await ctx.author.send('**Not Yet Implemented**')
        else:
            return await ctx.author.send('**ERROR** - Not a valid choice.')

    async def travel(self, ctx):
        return await ctx.author.send('**Not Yet Implemented**')

    async def modify_ship(self, ctx):
        return await ctx.author.send('**Not Yet Implemented**')

    async def change_ship(self, ctx):
        return await ctx.author.send('**Not Yet Implemented**')

    async def visit_market(self, ctx):
        return await ctx.author.send('**Not Yet Implemented**')

