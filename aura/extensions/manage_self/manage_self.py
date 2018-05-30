from discord.ext import commands
from aura.lib import db
from aura.lib import game_functions
from aura.lib import game_assets
from aura.core import checks
from aura.utils import make_embed


class ManageSelf:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session
        self.config = bot.config
        self.logger = bot.logger

    @commands.command(name='me', case_insensitive=True)
    @checks.spam_check()
    @checks.is_whitelist()
    @checks.has_account()
    async def _me(self, ctx):
        """Manage your character."""
        if ctx.guild is not None:
            await ctx.message.delete()
        sql = ''' SELECT * FROM eve_rpg_players WHERE `player_id` = (?) '''
        values = (ctx.message.author.id,)
        player = await db.select_var(sql, values)
        player_name = self.bot.get_user(int(player[0][2])).display_name
        region_id = int(player[0][4])
        sql = ''' SELECT * FROM eve_rpg_players WHERE `region` = (?) '''
        values = (region_id,)
        local_players = await db.select_var(sql, values)
        region_name = await game_functions.get_region(region_id)
        current_task = await game_functions.get_task(int(player[0][6]))
        current_ship_raw = await game_functions.get_ship_name(int(player[0][14]))
        current_ship = current_ship_raw
        wallet_balance = player[0][5]
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        if int(player[0][6]) == 20:
            destination = await game_functions.get_region(int(player[0][17]))
            embed.add_field(name="Welcome {}".format(player_name),
                            value="**Current Region** - {}\n**Local Count** - {}\n**Current Ship** - {}\n"
                                  "**Current Task** - {}\n**Wallet Balance** - {}\n\n"
                                  "*Ship is currently traveling to {}.......*".format(
                                region_name, len(local_players), current_ship, current_task, wallet_balance, destination))
            return await ctx.author.send(embed=embed)
        embed.add_field(name="Welcome {}".format(player_name),
                        value="**Current Region** - {}\n**Local Count** - {}\n**Current Ship** - {}\n"
                              "**Current Task** - {}\n**Wallet Balance** - {}\n\n"
                              "*User interface initiated.... Select desired action below......*\n\n"
                              "**1.** Change task.\n"
                              "**2.** Travel to a new region.\n"
                              "**3.** Modify current ship.\n"
                              "**4.** Change into another ship.\n"
                              "**5.** Visit the regional market.\n".format(
                            region_name, len(local_players), current_ship, current_task, wallet_balance))
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120.0)
        content = msg.content
        if content == '1':
            await self.change_task(ctx, player)
        elif content == '2':
            await self.travel(ctx, region_id, region_name)
        elif content == '3':
            await self.modify_ship(ctx)
        elif content == '4':
            await self.change_ship(ctx)
        elif content == '5':
            await self.visit_market(ctx, player)
        else:
            return await ctx.author.send('**ERROR** - Not a valid choice.')

    async def change_task(self, ctx, player):
        region_id = int(player[0][4])
        region_security = await game_functions.get_region_security(region_id)
        current_task = await game_functions.get_task(int(player[0][6]))
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        if region_security != 'High':
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
                                  "**9.** Mine an asteroid belt.\n"
                                  "**10.** Mine a mining anomaly.\n".format(current_task))
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
                                  "**Mining Tasks**\n"
                                  "**9.** Mine an asteroid belt.\n".format(current_task))
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120.0)
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

    async def travel(self, ctx, region_id, region_name):
        connected_regions = []
        region_connections = await game_functions.get_region_connections(region_id)
        for regions in region_connections:
            name = await game_functions.get_region(regions)
            sec = await  game_functions.get_region_security(regions)
            connected_regions.append('**{}.** {} ({} Sec)'.format(regions, name, sec))
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
        if 0 < int(content) < 13:
            sql = ''' UPDATE eve_rpg_players
                    SET destination = (?),
                        task = 20
                    WHERE
                        player_id = (?); '''
            values = (int(content), ctx.author.id,)
            destination = await game_functions.get_region(int(content))
            await db.execute_sql(sql, values)
            return await ctx.author.send('**Task Updated** - You are now traveling to {}.'.format(destination))
        elif content == '5':
            return await ctx.author.send('**Not Yet Implemented**')
        else:
            return await ctx.author.send('**ERROR** - Not a valid choice.')

    async def modify_ship(self, ctx):
        return await ctx.author.send('**Not Yet Implemented**')

    async def change_ship(self, ctx):
        return await ctx.author.send('**Not Yet Implemented**')

    async def visit_market(self, ctx, player):
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
                if ship['class'] == 2:
                    frigates.append('**{}.** {} - {} ISK'.format(ship['id'], ship['name'], ship['isk']))
                elif ship['class'] == 3:
                    destroyers.append('**{}.** {} - {} ISK'.format(ship['id'], ship['name'], ship['isk']))
                elif ship['class'] == 4:
                    tactical_destroyers.append('**{}.** {} - {} ISK'.format(ship['id'], ship['name'], ship['isk']))
                elif ship['class'] == 5:
                    interceptors.append('**{}.** {} - {} ISK'.format(ship['id'], ship['name'], ship['isk']))
                elif ship['class'] == 6:
                    mining_frigate.append('**{}.** {} - {} ISK'.format(ship['id'], ship['name'], ship['isk']))
                elif ship['class'] == 7:
                    mining_barges.append('**{}.** {} - {} ISK'.format(ship['id'], ship['name'], ship['isk']))
                elif ship['class'] == 8:
                    exhumers.append('**{}.** {} - {} ISK'.format(ship['id'], ship['name'], ship['isk']))
            merged = frigates + destroyers + interceptors + tactical_destroyers + mining_frigate + mining_barges + \
                     exhumers
            ship_list = '\n'.join(merged)
            embed = make_embed(icon=ctx.bot.user.avatar)
            embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                             text="Aura - EVE Text RPG")
            embed.add_field(name="Ship Market",
                            value="Wallet - {} ISK \n\n {}".format(player[0][5], ship_list))
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
                sql = ''' UPDATE eve_rpg_players
                        SET ship = (?),
                            isk = (?)
                        WHERE
                            player_id = (?); '''
                remaining_isk = int(player[0][5]) - int(ship['isk'])
                values = (int(ship['id']), remaining_isk, ctx.author.id,)
                await db.execute_sql(sql, values)
                return await ctx.author.send('**{} Purchase Complete**'.format(ship['name']))
            return await ctx.author.send('**ERROR** - Not a valid choice.')

        elif content == '2':
            return await ctx.author.send('**Not Yet Implemented**')
        elif content == '3':
            return await ctx.author.send('**Not Yet Implemented**')
        else:
            return await ctx.author.send('**ERROR** - Not a valid choice.')
