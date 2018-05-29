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
        current_ship = player[0][15]
        wallet_balance = player[0][5]
        current_task = await game_functions.get_task(int(player[0][6]))
        current_focus = await game_functions.get_focus(int(player[0][7]))
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Welcome {}".format(player_name),
                        value="**Current Region** - {}\n**Current Ship** - {}\n**Current Task** - {}\n"
                              "**Current Focus** - {}\n**Wallet Balance** - {}\n\n"
                              "*User interface initiated.... Select desired action below......*\n\n"
                              "**1.** Change task\n"
                              "**2.** Travel to a new region.\n"
                              "**3.** Modify current ship.\n"
                              "**4.** Change into another ship.\n"
                              "**5.** Visit the regional market.\n"
                              "**6.** Change focus\n".format(
                            region_name, current_ship, current_task, current_focus, wallet_balance))
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author

        msg = await self.bot.wait_for('message', check=check, timeout=60.0)
        content = msg.content
        if content == '1':
            await self.change_task(ctx)
        elif content == '2':
            await self.travel(ctx)
        elif content == '3':
            await self.modify_ship(ctx)
        elif content == '4':
            await self.change_ship(ctx)
        elif content == '5':
            await self.visit_market(ctx)
        elif content == '6':
            await self.change_focus(ctx)
        else:
            return await ctx.author.send('**ERROR** - Not a valid choice.')

    async def change_task(self, ctx):
        return await ctx.author.send('**Not Yet Implemented**')

    async def travel(self, ctx):
        return await ctx.author.send('**Not Yet Implemented**')

    async def modify_ship(self, ctx):
        return await ctx.author.send('**Not Yet Implemented**')

    async def change_ship(self, ctx):
        return await ctx.author.send('**Not Yet Implemented**')

    async def visit_market(self, ctx):
        return await ctx.author.send('**Not Yet Implemented**')

    async def change_focus(self, ctx):
        return await ctx.author.send('**Not Yet Implemented**')

