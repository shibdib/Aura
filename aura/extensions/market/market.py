from discord.ext import commands
from aura.lib import db
from aura.lib import game_functions
from aura.lib import game_assets
from aura.core import checks
from aura.utils import make_embed


class Market:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session
        self.config = bot.config
        self.logger = bot.logger

    @commands.command(name='market', case_insensitive=True)
    @checks.spam_check()
    @checks.is_whitelist()
    @checks.has_account()
    async def visit_market(self, ctx):
        """Visit the regional marketplace."""
        if ctx.guild is not None:
            await ctx.message.delete()
        sql = ''' SELECT * FROM eve_rpg_players WHERE `player_id` = (?) '''
        values = (ctx.message.author.id,)
        player = await db.select_var(sql, values)
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Select Market",
                        value="**1.** Ships.\n"
                              "**2.** Modules.\n"
                              "**3.** Components.\n")
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author

        msg = await self.bot.wait_for('message', check=check, timeout=60.0)
        content = msg.content
        if content == '1':
            ships_sale = []
            ships = game_assets.ships
            for key, ship in ships.items():
                ships_sale.append('**{}.** {} - {} ISK'.format(ship['id'], ship['name'], ship['isk']))
            ship_list = '\n'.join(ships_sale)
            embed = make_embed(icon=ctx.bot.user.avatar)
            embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                             text="Aura - EVE Text RPG")
            embed.add_field(name="Ship Market",
                            value="{}".format(ship_list))
            await ctx.author.send(embed=embed)

            def check(m):
                return m.author == ctx.author

            msg = await self.bot.wait_for('message', check=check, timeout=60.0)
            content = msg.content
            ship = await game_functions.get_ship(int(content))
            if ship is not None:
                if int(ship['isk']) > int(player[0][5]):
                    return await ctx.author.send('**Not Enough Isk**')
                embed = make_embed(icon=self.bot.user.avatar)
                embed.set_footer(icon_url=self.bot.user.avatar_url,
                                 text="Aura - EVE Text RPG")
                embed.set_thumbnail(url="{}".format(ship['image']))
                embed.add_field(name="Confirm Purchase",
                                value="Are you sure you want to buy a **{}** for {} ISK\n\n"
                                      "**1.** Yes.\n"
                                      "**2.** No.\n".format(ship['name'], ship['isk']))
                await ctx.author.send(embed=embed)

                def check(m):
                    return m.author == ctx.author

                msg = await self.bot.wait_for('message', check=check, timeout=60.0)
                content = msg.content
                if content != '1':
                    return await ctx.author.send('**Purchase Canceled**')
                sql = ''' UPDATE eve_rpg_players
                        SET ship = (?)
                        WHERE
                            player_id = (?); '''
                values = (int(ship['id']), ctx.author.id,)
                await db.execute_sql(sql, values)
                return await ctx.author.send('**{} Purchase Complete**'.format(ship['name']))
            return await ctx.author.send('**ERROR** - Not a valid choice.')

        elif content == '2':
            return await ctx.author.send('**Not Yet Implemented**')
        elif content == '3':
            return await ctx.author.send('**Not Yet Implemented**')
        else:
            return await ctx.author.send('**ERROR** - Not a valid choice.')
