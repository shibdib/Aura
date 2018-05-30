import ast

from discord.ext import commands

from aura.core import checks
from aura.lib import db
from aura.lib import game_assets
from aura.lib import game_functions
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
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120.0)
        content = msg.content
        wallet_balance = '{0:,.2f}'.format(float(player[0][5]))
        if content == '1':
            frigates = ['__**Frigates**__']
            destroyers = ['__**Destroyers**__']
            tactical_destroyers = ['__**Tactical Destroyers**__']
            interceptors = ['__**Interceptors**__']
            mining_frigate = ['__**Mining Frigates**__']
            mining_barges = ['__**Mining Barges**__']
            exhumers = ['__**Exhumers**__']
            ships = game_assets.ships
            for key, ship in ships.items():
                cost = '{0:,.2f}'.format(float(ship['isk']))
                if ship['class'] == 2:
                    frigates.append('**{}.** {} - {} ISK'.format(ship['id'], ship['name'], cost))
                elif ship['class'] == 3:
                    destroyers.append('**{}.** {} - {} ISK'.format(ship['id'], ship['name'], cost))
                elif ship['class'] == 4:
                    tactical_destroyers.append('**{}.** {} - {} ISK'.format(ship['id'], ship['name'], cost))
                elif ship['class'] == 5:
                    interceptors.append('**{}.** {} - {} ISK'.format(ship['id'], ship['name'], cost))
                elif ship['class'] == 6:
                    mining_frigate.append('**{}.** {} - {} ISK'.format(ship['id'], ship['name'], cost))
                elif ship['class'] == 7:
                    mining_barges.append('**{}.** {} - {} ISK'.format(ship['id'], ship['name'], cost))
                elif ship['class'] == 8:
                    exhumers.append('**{}.** {} - {} ISK'.format(ship['id'], ship['name'], cost))
            merged = frigates + destroyers + interceptors + tactical_destroyers + mining_frigate + mining_barges + \
                     exhumers
            ship_list = '\n'.join(merged)
            embed = make_embed(icon=ctx.bot.user.avatar)
            embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                             text="Aura - EVE Text RPG")
            embed.add_field(name="Ship Market",
                            value="Wallet - {} ISK \n\n {}".format(wallet_balance, ship_list))
            await ctx.author.send(embed=embed)

            def check(m):
                return m.author == ctx.author and m.channel == ctx.author.dm_channel

            msg = await self.bot.wait_for('message', check=check, timeout=120.0)
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
                    return m.author == ctx.author and m.channel == ctx.author.dm_channel

                msg = await self.bot.wait_for('message', check=check, timeout=120.0)
                content = msg.content
                if content != '1':
                    return await ctx.author.send('**Purchase Canceled**')
                if player[0][15] is None:
                    current_hangar = "{{}: [{}]}".format(player[0][4], ship['id'])
                elif player[0][15][player[0][4]] is None:
                    current_hangar = ast.literal_eval(player[0][15])
                    current_hangar[player[0][4]] = "[{}]".format(ship['id'])
                else:
                    current_hangar = ast.literal_eval(player[0][15])
                    current_hangar[player[0][4]].append(ship['id'])
                sql = ''' UPDATE eve_rpg_players
                        SET ship_hangar = (?),
                            isk = (?)
                        WHERE
                            player_id = (?); '''
                remaining_isk = int(player[0][5]) - int(ship['isk'])
                values = (current_hangar, remaining_isk, ctx.author.id,)
                await db.execute_sql(sql, values)
                return await ctx.author.send('**{} Purchase Complete, It Is Now Stored In Your Ship Hangar For This '
                                             'Region**'.format(ship['name']))
            return await ctx.author.send('**ERROR** - Not a valid choice.')

        elif content == '2':
            return await ctx.author.send('**Not Yet Implemented**')
        elif content == '3':
            return await ctx.author.send('**Not Yet Implemented**')
        else:
            return await ctx.author.send('**ERROR** - Not a valid choice.')
