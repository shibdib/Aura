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
        embed.add_field(name="Select Market Task",
                        value="**1.** Buy\n"
                              "**2.** Sell\n")
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120.0)
        content = msg.content

        if content == '1':
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
                accepted_options = []
                for key, ship in ships.items():
                    accepted_options.append(ship['id'])
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
                if int(content) in accepted_options:
                    ship = await game_functions.get_ship(int(content))
                    cost = '{0:,.2f}'.format(float(ship['isk']))
                    if int(ship['isk']) > int(player[0][5]):
                        return await ctx.author.send('**Not Enough Isk**')
                    embed = make_embed(icon=self.bot.user.avatar)
                    embed.set_footer(icon_url=self.bot.user.avatar_url,
                                     text="Aura - EVE Text RPG")
                    embed.set_thumbnail(url="{}".format(ship['image']))
                    embed.add_field(name="Confirm Purchase",
                                    value="Are you sure you want to buy a **{}** for {} ISK\n\n"
                                          "**1.** Yes.\n"
                                          "**2.** No.\n".format(ship['name'], cost))
                    await ctx.author.send(embed=embed)

                    def check(m):
                        return m.author == ctx.author and m.channel == ctx.author.dm_channel

                    msg = await self.bot.wait_for('message', check=check, timeout=120.0)
                    new_id = await game_functions.create_unique_id()
                    new_ship = {'id': new_id, 'ship_type': ship['id']}
                    content = msg.content
                    current_hangar = ast.literal_eval(player[0][15])
                    if content != '1':
                        return await ctx.author.send('**Purchase Canceled**')
                    if current_hangar is None:
                        current_hangar = {player[0][4]: [new_ship]}
                    elif player[0][4] not in current_hangar:
                        current_hangar[player[0][4]] = [new_ship]
                    else:
                        current_hangar[player[0][4]].append(new_ship)
                    sql = ''' UPDATE eve_rpg_players
                            SET ship_hangar = (?),
                                isk = (?)
                            WHERE
                                player_id = (?); '''
                    remaining_isk = int(player[0][5]) - int(ship['isk'])
                    values = (str(current_hangar), remaining_isk, ctx.author.id,)
                    await db.execute_sql(sql, values)
                    return await ctx.author.send(
                        '**{} Purchase Complete, It Is Now Stored In Your Ship Hangar For This '
                        'Region**'.format(ship['name']))
                return await ctx.author.send('**ERROR** - Not a valid choice.')
            elif content == '2':
                attack = ['__**Attack**__']
                defense = ['__**Defense**__']
                maneuver = ['__**Maneuver**__']
                tracking = ['__**Tracking**__']
                mining = ['__**Mining**__']
                modules = game_assets.modules
                for key, module in modules.items():
                    cost = '{0:,.2f}'.format(float(module['isk']))
                    if module['class'] == 1:
                        attack.append('**{}.** {} - {} ISK'.format(module['id'], module['name'], cost))
                    elif module['class'] == 2:
                        defense.append('**{}.** {} - {} ISK'.format(module['id'], module['name'], cost))
                    elif module['class'] == 3:
                        maneuver.append('**{}.** {} - {} ISK'.format(module['id'], module['name'], cost))
                    elif module['class'] == 4:
                        tracking.append('**{}.** {} - {} ISK'.format(module['id'], module['name'], cost))
                    elif module['class'] == 5:
                        mining.append('**{}.** {} - {} ISK'.format(module['id'], module['name'], cost))
                merged = attack + defense + maneuver + tracking + mining
                module_list = '\n'.join(merged)
                embed = make_embed(icon=ctx.bot.user.avatar)
                embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                                 text="Aura - EVE Text RPG")
                embed.add_field(name="Module Market",
                                value="Wallet - {} ISK \n\n {}".format(wallet_balance, module_list))
                await ctx.author.send(embed=embed)

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.author.dm_channel

                msg = await self.bot.wait_for('message', check=check, timeout=120.0)
                content = msg.content
                module = await game_functions.get_module(int(content))
                if module is not None:
                    cost = '{0:,.2f}'.format(float(module['isk']))
                    if int(module['isk']) > int(player[0][5]):
                        return await ctx.author.send('**Not Enough Isk**')
                    embed = make_embed(icon=self.bot.user.avatar)
                    embed.set_footer(icon_url=self.bot.user.avatar_url,
                                     text="Aura - EVE Text RPG")
                    embed.set_thumbnail(url="{}".format(module['image']))
                    embed.add_field(name="Confirm Purchase",
                                    value="Are you sure you want to buy a **{}** for {} ISK\n\n"
                                          "**1.** Yes.\n"
                                          "**2.** No.\n".format(module['name'], cost))
                    await ctx.author.send(embed=embed)

                    def check(m):
                        return m.author == ctx.author and m.channel == ctx.author.dm_channel

                    msg = await self.bot.wait_for('message', check=check, timeout=120.0)
                    content = msg.content
                    if content != '1':
                        return await ctx.author.send('**Purchase Canceled**')
                    if player[0][13] is None:
                        current_hangar = {player[0][4]: [module['id']]}
                    else:
                        current_hangar = ast.literal_eval(player[0][13])
                        if player[0][4] not in current_hangar:
                            current_hangar[player[0][4]] = [module['id']]
                        else:
                            current_hangar[player[0][4]].append(module['id'])
                    sql = ''' UPDATE eve_rpg_players
                            SET module_hangar = (?),
                                isk = (?)
                            WHERE
                                player_id = (?); '''
                    remaining_isk = int(player[0][5]) - int(module['isk'])
                    values = (str(current_hangar), remaining_isk, ctx.author.id,)
                    await db.execute_sql(sql, values)
                    return await ctx.author.send(
                        '**{} Purchase Complete, It Is Now Stored In Your Module Hangar For This '
                        'Region**'.format(module['name']))
                return await ctx.author.send('**ERROR** - Not a valid choice.')
            elif content == '3':
                return await ctx.author.send('**Not Yet Implemented**')
            else:
                return await ctx.author.send('**ERROR** - Not a valid choice.')
        elif content == '2':
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
            region_id = int(player[0][4])
            region_name = await game_functions.get_region(region_id)
            if content == '1':
                ship_hangar = ast.literal_eval(player[0][15])
                if player[0][4] not in ship_hangar:
                    embed = make_embed(icon=ctx.bot.user.avatar)
                    embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                                     text="Aura - EVE Text RPG")
                    embed.add_field(name="{} Ship Hangar".format(region_name),
                                    value='No Ships Found In This Region')
                    return await ctx.author.send(embed=embed)
                stored_ships_array = []
                owned_ship_ids = []
                ship_number = 1
                for ship in ship_hangar[player[0][4]]:
                    owned_ship_ids.append(ship_number)
                    ship['selection'] = ship_number
                    ship_info = await game_functions.get_ship(int(ship['ship_type']))
                    sale_price = '{0:,.2f}'.format(float(ship_info['isk'] * 0.95))
                    ship['sale_price'] = sale_price
                    stored_ships_array.append('{}. {} *({} ISK)*'.format(ship_number, ship_info['name'], sale_price))
                    ship_number += 1
                stored_ships = '\n'.join(stored_ships_array)
                embed = make_embed(icon=ctx.bot.user.avatar)
                embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                                 text="Aura - EVE Text RPG")
                embed.add_field(name="{} Ship Hangar".format(region_name),
                                value=stored_ships)
                await ctx.author.send(embed=embed)

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.author.dm_channel

                msg = await self.bot.wait_for('message', check=check, timeout=120.0)
                content = msg.content
                if int(content) in owned_ship_ids:
                    for ship in ship_hangar[player[0][4]]:
                        if ship['selection'] == int(content):
                            ship_id = ship['id']
                            selected_ship = await game_functions.get_ship(int(ship['ship_type']))
                            sale_price = ship['sale_price']
                    embed = make_embed(icon=self.bot.user.avatar)
                    embed.set_footer(icon_url=self.bot.user.avatar_url,
                                     text="Aura - EVE Text RPG")
                    embed.set_thumbnail(url="{}".format(selected_ship['image']))
                    embed.add_field(name="Confirm Sale",
                                    value="Are you sure you want to sell a **{}** for {} ISK\n\n"
                                          "**1.** Yes.\n"
                                          "**2.** No.\n".format(selected_ship['name'], sale_price))
                    await ctx.author.send(embed=embed)

                    def check(m):
                        return m.author == ctx.author and m.channel == ctx.author.dm_channel

                    msg = await self.bot.wait_for('message', check=check, timeout=120.0)
                    content = msg.content
                    if content != '1':
                        return await ctx.author.send('**Sale Canceled**')
                    for ship in ship_hangar[player[0][4]]:
                        if ship['id'] == ship_id:
                            remove = ship
                            break
                    ship_hangar[player[0][4]].remove(remove)
                    new_hangar = ship_hangar
                    new_isk = float(player[0][5]) + float(sale_price)
                    if None is not None:
                        if player[0][13] is not None and player[0][4] in ast.literal_eval(player[0][13]):
                            module_hangar = ast.literal_eval(player[0][13])
                            for module in ast.literal_eval(player[0][12]):
                                module_hangar[player[0][4]].append(module)
                        elif player[0][13] is not None:
                            module_hangar = ast.literal_eval(player[0][13])
                            module_hangar[player[0][4]] = ast.literal_eval(player[0][12])
                        else:
                            modules = ast.literal_eval(player[0][12])
                            module_hangar = {player[0][4]: modules}
                        values = (str(new_hangar), str(module_hangar), int(new_isk), ctx.author.id,)
                    else:
                        values = (str(new_hangar), player[0][13], int(new_isk), ctx.author.id,)
                    sql = ''' UPDATE eve_rpg_players
                            SET ship_hangar = (?),
                                module_hangar = (?),
                                isk = (?)
                            WHERE
                                player_id = (?); '''
                    await db.execute_sql(sql, values)
                    return await ctx.author.send('**Sold a {} for {} ISK**'.format(selected_ship['name'], sale_price))
                else:
                    return await ctx.author.send('**ERROR** - Not a valid choice.')
            elif content == '2':
                module_hangar = ast.literal_eval(player[0][13])
                if player[0][4] not in module_hangar:
                    embed = make_embed(icon=ctx.bot.user.avatar)
                    embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                                     text="Aura - EVE Text RPG")
                    embed.add_field(name="{} Module Hangar".format(region_name),
                                    value='No Modules Found In This Region')
                    return await ctx.author.send(embed=embed)
                sell_module_order = {}
                stored_module_array = []
                owned_module_ids = []
                module_number = 1
                for module in module_hangar[player[0][4]]:
                    sell_module_order[module_number] = int(module)
                    owned_module_ids.append(module_number)
                    module_info = await game_functions.get_module(int(module))
                    sale_price = '{0:,.2f}'.format(float(module_info['isk'] * 0.95))
                    stored_module_array.append(
                        '{}. {} *({} ISK)*'.format(module_number, module_info['name'], sale_price))
                    module_number += 1
                stored_modules = '\n'.join(stored_module_array)
                embed = make_embed(icon=ctx.bot.user.avatar)
                embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                                 text="Aura - EVE Text RPG")
                embed.add_field(name="{} Module Hangar".format(region_name),
                                value=stored_modules)
                await ctx.author.send(embed=embed)

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.author.dm_channel

                msg = await self.bot.wait_for('message', check=check, timeout=120.0)
                content = msg.content
                if int(content) in owned_module_ids:
                    module = sell_module_order[int(content)]
                    module_info = await game_functions.get_module(int(module))
                    sale_price = '{0:,.2f}'.format(float(module_info['isk'] * 0.95))
                    embed = make_embed(icon=self.bot.user.avatar)
                    embed.set_footer(icon_url=self.bot.user.avatar_url,
                                     text="Aura - EVE Text RPG")
                    embed.set_thumbnail(url="{}".format(module_info['image']))
                    embed.add_field(name="Confirm Sale",
                                    value="Are you sure you want to sell a **{}** for {} ISK\n\n"
                                          "**1.** Yes.\n"
                                          "**2.** No.\n".format(module_info['name'], sale_price))
                    await ctx.author.send(embed=embed)

                    def check(m):
                        return m.author == ctx.author and m.channel == ctx.author.dm_channel

                    msg = await self.bot.wait_for('message', check=check, timeout=120.0)
                    content = msg.content
                    if content != '1':
                        return await ctx.author.send('**Sale Canceled**')
                    module_hangar[player[0][4]].remove(sell_module_order[int(content)])
                    new_hangar = module_hangar
                    new_isk = float(player[0][5]) + float(sale_price)
                    values = (str(new_hangar), int(new_isk), ctx.author.id,)
                    sql = ''' UPDATE eve_rpg_players
                            SET module_hangar = (?),
                                isk = (?)
                            WHERE
                                player_id = (?); '''
                    await db.execute_sql(sql, values)
                    return await ctx.author.send('**Sold a {} for {} ISK**'.format(module_info['name'], sale_price))
                else:
                    return await ctx.author.send('**ERROR** - Not a valid choice.')
            elif content == '3':
                return await ctx.author.send('**ERROR** - Not yet implemented.')
            else:
                return await ctx.author.send('**ERROR** - Not a valid choice.')
        else:
            return await ctx.author.send('**ERROR** - Not a valid choice.')
