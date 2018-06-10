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
            try:
                await ctx.message.delete()
            except Exception:
                pass
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
            player_ship_obj = ast.literal_eval(player[0][14])
            wallet_balance = '{0:,.2f}'.format(float(player[0][5]))
            if content == '1':
                frigates = ['__**Frigates**__']
                destroyers = ['__**Destroyers**__']
                cruisers = ['__**Cruisers**__']
                battlecruisers = ['__**Battlecruisers**__']
                battleships = ['__**Battleships**__']
                tactical_destroyers = ['__**Tactical Destroyers**__']
                interceptors = ['__**Interceptors**__']
                mining_frigate = ['__**Mining Frigates**__']
                mining_barges = ['__**Mining Barges**__']
                exhumers = ['__**Exhumers**__']
                ships = game_assets.ships
                ship_number = 1
                ship_assigned_number = {}
                accepted_options = []
                for key, ship in ships.items():
                    cost = '{0:,.2f}'.format(float(ship['isk']))
                    if ship['class'] == 1:
                        frigates.append(
                            '**{}.** {} ({} HP) ({}/{}/{}/{}) - *Drone Bay Size: {}m3* - {} ISK'.format(ship_number,
                                                                                                        ship[
                                                                                                            'name'],
                                                                                                        ship[
                                                                                                            'hit_points'],
                                                                                                        ship[
                                                                                                            'attack'],
                                                                                                        ship[
                                                                                                            'defense'],
                                                                                                        ship[
                                                                                                            'maneuver'],
                                                                                                        ship[
                                                                                                            'tracking'],
                                                                                                        ship[
                                                                                                            'drone_bay'],
                                                                                                        cost))
                        ship_assigned_number[ship_number] = ship['id']
                        accepted_options.append(ship_number)
                        ship_number += 1
                    elif ship['class'] == 3:
                        destroyers.append(
                            '**{}.** {} ({} HP) ({}/{}/{}/{}) - *Drone Bay Size: {}m3* - {} ISK'.format(ship_number,
                                                                                                        ship[
                                                                                                            'name'],
                                                                                                        ship[
                                                                                                            'hit_points'],
                                                                                                        ship[
                                                                                                            'attack'],
                                                                                                        ship[
                                                                                                            'defense'],
                                                                                                        ship[
                                                                                                            'maneuver'],
                                                                                                        ship[
                                                                                                            'tracking'],
                                                                                                        ship[
                                                                                                            'drone_bay'],
                                                                                                        cost))
                        ship_assigned_number[ship_number] = ship['id']
                        accepted_options.append(ship_number)
                        ship_number += 1
                    elif ship['class'] == 4:
                        tactical_destroyers.append(
                            '**{}.** {} ({} HP) ({}/{}/{}/{}) - *Drone Bay Size: {}m3* - {} ISK'.format(ship_number,
                                                                                                        ship[
                                                                                                            'name'],
                                                                                                        ship[
                                                                                                            'hit_points'],
                                                                                                        ship[
                                                                                                            'attack'],
                                                                                                        ship[
                                                                                                            'defense'],
                                                                                                        ship[
                                                                                                            'maneuver'],
                                                                                                        ship[
                                                                                                            'tracking'],
                                                                                                        ship[
                                                                                                            'drone_bay'],
                                                                                                        cost))
                        ship_assigned_number[ship_number] = ship['id']
                        accepted_options.append(ship_number)
                        ship_number += 1
                    elif ship['class'] == 2:
                        interceptors.append(
                            '**{}.** {} ({} HP) ({}/{}/{}/{}) - *Drone Bay Size: {}m3* - {} ISK'.format(ship_number,
                                                                                                        ship[
                                                                                                            'name'],
                                                                                                        ship[
                                                                                                            'hit_points'],
                                                                                                        ship[
                                                                                                            'attack'],
                                                                                                        ship[
                                                                                                            'defense'],
                                                                                                        ship[
                                                                                                            'maneuver'],
                                                                                                        ship[
                                                                                                            'tracking'],
                                                                                                        ship[
                                                                                                            'drone_bay'],
                                                                                                        cost))
                        ship_assigned_number[ship_number] = ship['id']
                        accepted_options.append(ship_number)
                        ship_number += 1
                    elif ship['class'] == 5:
                        cruisers.append(
                            '**{}.** {} ({} HP) ({}/{}/{}/{}) - *Drone Bay Size: {}m3* - {} ISK'.format(ship_number,
                                                                                                        ship[
                                                                                                            'name'],
                                                                                                        ship[
                                                                                                            'hit_points'],
                                                                                                        ship[
                                                                                                            'attack'],
                                                                                                        ship[
                                                                                                            'defense'],
                                                                                                        ship[
                                                                                                            'maneuver'],
                                                                                                        ship[
                                                                                                            'tracking'],
                                                                                                        ship[
                                                                                                            'drone_bay'],
                                                                                                        cost))
                        ship_assigned_number[ship_number] = ship['id']
                        accepted_options.append(ship_number)
                        ship_number += 1
                    elif ship['class'] == 6:
                        battlecruisers.append(
                            '**{}.** {} ({} HP) ({}/{}/{}/{}) - *Drone Bay Size: {}m3* - {} ISK'.format(ship_number,
                                                                                                        ship[
                                                                                                            'name'],
                                                                                                        ship[
                                                                                                            'hit_points'],
                                                                                                        ship[
                                                                                                            'attack'],
                                                                                                        ship[
                                                                                                            'defense'],
                                                                                                        ship[
                                                                                                            'maneuver'],
                                                                                                        ship[
                                                                                                            'tracking'],
                                                                                                        ship[
                                                                                                            'drone_bay'],
                                                                                                        cost))
                        ship_assigned_number[ship_number] = ship['id']
                        accepted_options.append(ship_number)
                        ship_number += 1
                    elif ship['class'] == 7:
                        battleships.append(
                            '**{}.** {} ({} HP) ({}/{}/{}/{}) - *Drone Bay Size: {}m3* - {} ISK'.format(ship_number,
                                                                                                        ship[
                                                                                                            'name'],
                                                                                                        ship[
                                                                                                            'hit_points'],
                                                                                                        ship[
                                                                                                            'attack'],
                                                                                                        ship[
                                                                                                            'defense'],
                                                                                                        ship[
                                                                                                            'maneuver'],
                                                                                                        ship[
                                                                                                            'tracking'],
                                                                                                        ship[
                                                                                                            'drone_bay'],
                                                                                                        cost))
                        ship_assigned_number[ship_number] = ship['id']
                        accepted_options.append(ship_number)
                        ship_number += 1
                    elif ship['class'] == 21:
                        mining_frigate.append(
                            '**{}.** {} ({} HP) ({}/{}/{}/{}) - *Drone Bay Size: {}m3* - {} ISK'.format(ship_number,
                                                                                                        ship[
                                                                                                            'name'],
                                                                                                        ship[
                                                                                                            'hit_points'],
                                                                                                        ship[
                                                                                                            'attack'],
                                                                                                        ship[
                                                                                                            'defense'],
                                                                                                        ship[
                                                                                                            'maneuver'],
                                                                                                        ship[
                                                                                                            'tracking'],
                                                                                                        ship[
                                                                                                            'drone_bay'],
                                                                                                        cost))
                        ship_assigned_number[ship_number] = ship['id']
                        accepted_options.append(ship_number)
                        ship_number += 1
                    elif ship['class'] == 22:
                        mining_barges.append(
                            '**{}.** {} ({} HP) ({}/{}/{}/{}) - *Drone Bay Size: {}m3* - {} ISK'.format(ship_number,
                                                                                                        ship[
                                                                                                            'name'],
                                                                                                        ship[
                                                                                                            'hit_points'],
                                                                                                        ship[
                                                                                                            'attack'],
                                                                                                        ship[
                                                                                                            'defense'],
                                                                                                        ship[
                                                                                                            'maneuver'],
                                                                                                        ship[
                                                                                                            'tracking'],
                                                                                                        ship[
                                                                                                            'drone_bay'],
                                                                                                        cost))
                        ship_assigned_number[ship_number] = ship['id']
                        accepted_options.append(ship_number)
                        ship_number += 1
                    elif ship['class'] == 23:
                        exhumers.append(
                            '**{}.** {} ({} HP) ({}/{}/{}/{}) - *Drone Bay Size: {}m3* - {} ISK'.format(ship_number,
                                                                                                        ship[
                                                                                                            'name'],
                                                                                                        ship[
                                                                                                            'hit_points'],
                                                                                                        ship[
                                                                                                            'attack'],
                                                                                                        ship[
                                                                                                            'defense'],
                                                                                                        ship[
                                                                                                            'maneuver'],
                                                                                                        ship[
                                                                                                            'tracking'],
                                                                                                        ship[
                                                                                                            'drone_bay'],
                                                                                                        cost))
                        ship_assigned_number[ship_number] = ship['id']
                        accepted_options.append(ship_number)
                        ship_number += 1
                merged = frigates + interceptors
                merged_two = destroyers + tactical_destroyers
                merged_three = cruisers
                merged_four = battlecruisers
                merged_five = battleships
                merged_mining = mining_frigate + mining_barges + exhumers
                ship_list = '\n'.join(merged)
                ship_list_two = '\n'.join(merged_two)
                ship_list_three = '\n'.join(merged_three)
                ship_list_four = '\n'.join(merged_four)
                ship_list_five = '\n'.join(merged_five)
                ship_list_mining = '\n'.join(merged_mining)
                embed = make_embed(icon=ctx.bot.user.avatar)
                embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                                 text="Aura - EVE Text RPG")
                embed.add_field(name="Ship Market",
                                value="Wallet - {} ISK  \n\nAttributes (Attack/Defense/Maneuver/Tracking)\n".format(
                                    wallet_balance))
                embed.add_field(name="Frigates and Interceptors",
                                value="{}\n".format(ship_list))
                embed.add_field(name="Destroyers and Tactical Destroyers",
                                value="{}\n".format(ship_list_two))
                embed.add_field(name="Cruisers",
                                value="{}\n".format(ship_list_three))
                embed.add_field(name="Battlecruisers",
                                value="{}\n".format(ship_list_four))
                embed.add_field(name="Battleships",
                                value="{}\n".format(ship_list_five))
                embed.add_field(name="Mining Ships",
                                value="{}\n".format(ship_list_mining))
                await ctx.author.send(embed=embed)

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.author.dm_channel

                msg = await self.bot.wait_for('message', check=check, timeout=120.0)
                content = msg.content
                if int(content) in accepted_options:
                    ship = await game_functions.get_ship(ship_assigned_number[int(content)])
                    cost = '{0:,.2f}'.format(float(ship['isk']))
                    if int(float(ship['isk'])) > int(float(player[0][5])):
                        return await ctx.author.send('**Not Enough Isk**')
                    embed = make_embed(icon=self.bot.user.avatar)
                    embed.set_footer(icon_url=self.bot.user.avatar_url,
                                     text="Aura - EVE Text RPG")
                    embed.set_thumbnail(url="{}".format(ship['image']))
                    embed.add_field(name="Confirm Purchase",
                                    value="Are you sure you want to buy a **{}** for {} ISK\n\n"
                                          "**1.** Yes.\n"
                                          "**2.** No.\n"
                                          "**3.** Yes and make it my active ship.\n".format(ship['name'], cost))
                    await ctx.author.send(embed=embed)

                    def check(m):
                        return m.author == ctx.author and m.channel == ctx.author.dm_channel

                    msg = await self.bot.wait_for('message', check=check, timeout=120.0)
                    new_id = await game_functions.create_unique_id()
                    new_ship = {'id': new_id, 'ship_type': ship['id']}
                    content = msg.content
                    if content != '1' and content != '3':
                        await ctx.author.send('**Purchase Canceled**')
                    if content == '1':
                        if player[0][15] is None:
                            current_hangar = {player[0][4]: [new_ship]}
                        elif player[0][4] not in ast.literal_eval(player[0][15]):
                            current_hangar = ast.literal_eval(player[0][15])
                            current_hangar[player[0][4]] = [new_ship]
                        else:
                            current_hangar = ast.literal_eval(player[0][15])
                            current_hangar[player[0][4]].append(new_ship)
                        sql = ''' UPDATE eve_rpg_players
                                SET ship_hangar = (?),
                                    isk = (?)
                                WHERE
                                    player_id = (?); '''
                        remaining_isk = int(float(player[0][5])) - int(float(ship['isk']))
                        await self.update_journal(player[0], int(float(ship['isk'])) * -1)
                        values = (str(current_hangar), remaining_isk, ctx.author.id,)
                        await db.execute_sql(sql, values)
                        await ctx.author.send(
                            '**{} Purchase Complete, It Is Now Stored In Your Ship Hangar For This '
                            'Region**'.format(ship['name']))
                    elif content == '3':
                        if player[0][12] is not None:
                            old_modules = ast.literal_eval(player[0][12])
                            player_ship_obj['modules'] = old_modules
                        elif 'modules' in player_ship_obj:
                            player_ship_obj['modules'] = None
                        if player[0][15] is None:
                            current_hangar = {player[0][4]: [player_ship_obj]}
                        elif player[0][4] not in ast.literal_eval(player[0][15]):
                            current_hangar = ast.literal_eval(player[0][15])
                            current_hangar[player[0][4]] = [player_ship_obj]
                        else:
                            current_hangar = ast.literal_eval(player[0][15])
                            current_hangar[player[0][4]].append(player_ship_obj)
                        await self.update_journal(player[0], int(float(ship['isk'])) * -1)
                        sql = ''' UPDATE eve_rpg_players
                                SET ship = (?),
                                    modules = (?),
                                    ship_hangar = (?),
                                    isk = (?),
                                    task = 1
                                WHERE
                                    player_id = (?); '''
                        remaining_isk = int(float(player[0][5])) - int(float(ship['isk']))
                        values = (str(new_ship), None, str(current_hangar), remaining_isk, ctx.author.id,)
                        await db.execute_sql(sql, values)
                        await ctx.author.send(
                            '**{} Purchase Complete, It Is Now Your Active Ship**'.format(ship['name']))
                    return await ctx.invoke(self.bot.get_command("me"), True)
                await ctx.author.send('**ERROR** - Not a valid choice.')
                if content.find('!!') == -1:
                    return await ctx.invoke(self.bot.get_command("me"), True)
                else:
                    return
            elif content == '2':
                attack = ['__**Attack**__']
                defense = ['__**Defense**__']
                maneuver = ['__**Maneuver**__']
                tracking = ['__**Tracking**__']
                mining = ['__**Mining**__']
                other = ['__**Other**__']
                lights = ['__**Light Drones**__']
                mediums = ['__**Medium Drones**__']
                mining_drones = ['__**Mining Drones**__']
                modules = game_assets.modules
                accepted_modules = []
                module_selection_dict = {}
                module_number = 1
                for key, module in modules.items():
                    cost = '{0:,.2f}'.format(float(module['isk']))
                    if module['class'] == 1:
                        attack.append('**{}.** {} ({}%/{}%/{}%/{}%) - {} ISK'.format(module_number, module['name'],
                                                                                     module['attack'] * 100,
                                                                                     module['defense'] * 100,
                                                                                     module['maneuver'] * 100,
                                                                                     module['tracking'] * 100, cost))
                        module_selection_dict[module_number] = module['id']
                        accepted_modules.append(module_number)
                        module_number += 1
                    elif module['class'] == 2:
                        defense.append('**{}.** {} ({}%/{}%/{}%/{}%) - {} ISK'.format(module_number, module['name'],
                                                                                      module['attack'] * 100,
                                                                                      module['defense'] * 100,
                                                                                      module['maneuver'] * 100,
                                                                                      module['tracking'] * 100, cost))
                        module_selection_dict[module_number] = module['id']
                        accepted_modules.append(module_number)
                        module_number += 1
                    elif module['class'] == 3:
                        maneuver.append('**{}.** {} ({}%/{}%/{}%/{}%) - {} ISK'.format(module_number, module['name'],
                                                                                       module['attack'] * 100,
                                                                                       module['defense'] * 100,
                                                                                       module['maneuver'] * 100,
                                                                                       module['tracking'] * 100, cost))
                        module_selection_dict[module_number] = module['id']
                        accepted_modules.append(module_number)
                        module_number += 1
                    elif module['class'] == 4:
                        tracking.append('**{}.** {} ({}%/{}%/{}%/{}%) - {} ISK'.format(module_number, module['name'],
                                                                                       module['attack'] * 100,
                                                                                       module['defense'] * 100,
                                                                                       module['maneuver'] * 100,
                                                                                       module['tracking'] * 100, cost))
                        module_selection_dict[module_number] = module['id']
                        accepted_modules.append(module_number)
                        module_number += 1
                    elif module['class'] == 5:
                        mining.append('**{}.** {} ({}%/{}%/{}%/{}%) - {} ISK'.format(module_number, module['name'],
                                                                                     module['attack'] * 100,
                                                                                     module['defense'] * 100,
                                                                                     module['maneuver'] * 100,
                                                                                     module['tracking'] * 100, cost))
                        module_selection_dict[module_number] = module['id']
                        accepted_modules.append(module_number)
                        module_number += 1
                    elif module['class'] == 6:
                        other.append('**{}.** {} ({}) - {} ISK'.format(module_number, module['name'],
                                                                       module['special'], cost))
                        module_selection_dict[module_number] = module['id']
                        accepted_modules.append(module_number)
                        module_number += 1
                    elif module['class'] == 10:
                        lights.append(
                            '**{}.** {} ({}/{}/{}/{}) - *Size: {}m3* - {} ISK'.format(module_number, module['name'],
                                                                                      module['attack'],
                                                                                      module['defense'],
                                                                                      module['maneuver'],
                                                                                      module['tracking'],
                                                                                      module['size'], cost))
                        module_selection_dict[module_number] = module['id']
                        accepted_modules.append(module_number)
                        module_number += 1
                    elif module['class'] == 11:
                        mediums.append(
                            '**{}.** {} ({}/{}/{}/{}) - *Size: {}m3* - {} ISK'.format(module_number, module['name'],
                                                                                      module['attack'],
                                                                                      module['defense'],
                                                                                      module['maneuver'],
                                                                                      module['tracking'],
                                                                                      module['size'], cost))
                        module_selection_dict[module_number] = module['id']
                        accepted_modules.append(module_number)
                        module_number += 1
                    elif module['class'] == 14:
                        mining_drones.append(
                            '**{}.** {} ({}) - *Size: {}m3* - {} ISK'.format(module_number, module['name'],
                                                                             module['special'], module['size'], cost))
                        module_selection_dict[module_number] = module['id']
                        accepted_modules.append(module_number)
                        module_number += 1
                merged = attack + defense
                merged_two = maneuver + tracking
                merged_three = mining
                merged_four = other
                merged_drones = lights
                merged_mediums = mediums
                merged_utility_drones = mining_drones
                module_list = '\n'.join(merged)
                module_list_two = '\n'.join(merged_two)
                module_list_three = '\n'.join(merged_three)
                module_list_four = '\n'.join(merged_four)
                drone_list = '\n'.join(merged_drones)
                medium_drone_list = '\n'.join(merged_mediums)
                utility_drone_list = '\n'.join(merged_utility_drones)
                embed = make_embed(icon=ctx.bot.user.avatar)
                embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                                 text="Aura - EVE Text RPG")
                embed.add_field(name="Module Market",
                                value="Wallet - {} ISK \n\nBonuses (Attack/Defense/Maneuver/Tracking)".format(
                                    wallet_balance))
                embed.add_field(name="Attack and Defense Mods",
                                value="{}\n".format(module_list))
                embed.add_field(name="Maneuver and Tracking Mods",
                                value="{}\n".format(module_list_two))
                embed.add_field(name="Mining Mods",
                                value="{}\n".format(module_list_three))
                embed.add_field(name="Other Mods",
                                value="{}\n".format(module_list_four))
                embed.add_field(name="Light Drones",
                                value="{}\n".format(drone_list))
                embed.add_field(name="Medium Drones",
                                value="{}\n".format(medium_drone_list))
                embed.add_field(name="Utility Drones",
                                value="{}\n".format(utility_drone_list))
                await ctx.author.send(embed=embed)

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.author.dm_channel

                msg = await self.bot.wait_for('message', check=check, timeout=120.0)
                module_array = list(set(ast.literal_eval('[{}]'.format(msg.content))))
                if type(module_array) is list and len(module_array) > 1:
                    purchase_text_array = []
                    purchase_items = []
                    total_isk = 0
                    for item in module_array:
                        module = await game_functions.get_module(module_selection_dict[int(item)])
                        total_isk += module['isk']
                        purchase_items.append(module['id'])
                        purchase_text_array.append('{}'.format(module['name']))
                    cost = '{0:,.2f}'.format(float(total_isk))
                    purchase_text = '\n'.join(purchase_text_array)
                    embed = make_embed(icon=self.bot.user.avatar)
                    embed.set_footer(icon_url=self.bot.user.avatar_url,
                                     text="Aura - EVE Text RPG")
                    embed.add_field(name="Confirm Purchase",
                                    value="__**Buy**__\n{}\n*For {} ISK*\n\n"
                                          "**1.** Yes.\n"
                                          "**2.** No.\n".format(purchase_text, cost))
                    await ctx.author.send(embed=embed)

                    def check(m):
                        return m.author == ctx.author and m.channel == ctx.author.dm_channel

                    msg = await self.bot.wait_for('message', check=check, timeout=120.0)
                    content = msg.content
                    if content != '1':
                        await ctx.author.send('**Purchase Canceled**')
                        if content.find('!!') == -1:
                            return await ctx.invoke(self.bot.get_command("me"), True)
                        else:
                            return
                    if total_isk > int(float(player[0][5])):
                        await ctx.author.send('**Not Enough ISK**')
                        return await ctx.invoke(self.bot.get_command("me"), True)
                    player = await game_functions.refresh_player(player[0])
                    for item in purchase_items:
                        module = await game_functions.get_module(item)
                        player = await game_functions.refresh_player(player)
                        if player[13] is None:
                            current_hangar = {player[4]: [item]}
                        else:
                            current_hangar = ast.literal_eval(player[13])
                            if player[4] not in current_hangar:
                                current_hangar[player[4]] = [item]
                            else:
                                current_hangar[player[4]].append(item)
                        sql = ''' UPDATE eve_rpg_players
                                SET module_hangar = (?),
                                    isk = (?)
                                WHERE
                                    player_id = (?); '''
                        remaining_isk = int(float(player[5])) - int(float(module['isk']))
                        values = (str(current_hangar), remaining_isk, ctx.author.id,)
                        await db.execute_sql(sql, values)
                    await ctx.author.send(
                        '**Purchase Complete, Items Are Now Stored In Your Module Hangar For This Region**')
                    await self.update_journal(player[0], float(total_isk) * -1)
                    return await ctx.invoke(self.bot.get_command("me"), True)
                item = msg.content
                if int(item) in accepted_modules:
                    module = await game_functions.get_module(module_selection_dict[int(item)])
                    embed = make_embed(icon=self.bot.user.avatar)
                    embed.set_footer(icon_url=self.bot.user.avatar_url,
                                     text="Aura - EVE Text RPG")
                    embed.set_thumbnail(url="{}".format(module['image']))
                    embed.add_field(name="Confirm Purchase",
                                    value="How many **{}** do you want to purchase?".format(module['name']))
                    await ctx.author.send(embed=embed)

                    def check(m):
                        return m.author == ctx.author and m.channel == ctx.author.dm_channel

                    msg = await self.bot.wait_for('message', check=check, timeout=120.0)
                    content = msg.content
                    if content == '0':
                        await ctx.author.send('**Purchase Canceled**')
                        if content.find('!!') == -1:
                            return await ctx.invoke(self.bot.get_command("me"), True)
                        else:
                            return
                    try:
                        int(content)
                    except ValueError:
                        await ctx.author.send('**Invalid Amount, Purchase Canceled**')
                        if content.find('!!') == -1:
                            return await ctx.invoke(self.bot.get_command("me"), True)
                        else:
                            return
                    amount = int(content)
                    cost = '{0:,.2f}'.format(float(module['isk']) * amount)
                    if int(float(module['isk']) * amount) > int(float(player[0][5])):
                        return await ctx.author.send('**Not Enough Isk**')
                    embed = make_embed(icon=self.bot.user.avatar)
                    embed.set_footer(icon_url=self.bot.user.avatar_url,
                                     text="Aura - EVE Text RPG")
                    embed.set_thumbnail(url="{}".format(module['image']))
                    embed.add_field(name="Confirm Purchase",
                                    value="Are you sure you want to buy {} **{}** for {} ISK\n\n"
                                          "**1.** Yes.\n"
                                          "**2.** No.\n".format(amount, module['name'], cost))
                    await ctx.author.send(embed=embed)

                    def check(m):
                        return m.author == ctx.author and m.channel == ctx.author.dm_channel

                    msg = await self.bot.wait_for('message', check=check, timeout=120.0)
                    content = msg.content
                    if content != '1':
                        await ctx.author.send('**Purchase Canceled**')
                        if content.find('!!') == -1:
                            return await ctx.invoke(self.bot.get_command("me"), True)
                        else:
                            return
                    player = await game_functions.refresh_player(player[0])
                    for x in range(amount):
                        player = await game_functions.refresh_player(player)
                        if player[13] is None:
                            current_hangar = {player[4]: [module['id']]}
                        else:
                            current_hangar = ast.literal_eval(player[13])
                            if player[4] not in current_hangar:
                                current_hangar[player[4]] = [module['id']]
                            else:
                                current_hangar[player[4]].append(module['id'])
                        await self.update_journal(player, int(float(module['isk'])) * -1)
                        sql = ''' UPDATE eve_rpg_players
                                SET module_hangar = (?),
                                    isk = (?)
                                WHERE
                                    player_id = (?); '''
                        remaining_isk = int(float(player[5])) - int(float(module['isk']))
                        values = (str(current_hangar), remaining_isk, ctx.author.id,)
                        await db.execute_sql(sql, values)
                    await ctx.author.send(
                        '**{} Purchase Complete, It Is Now Stored In Your Module Hangar For This '
                        'Region**'.format(module['name']))
                    return await ctx.invoke(self.bot.get_command("me"), True)
                await ctx.author.send('**ERROR** - Not a valid choice.')
            elif content == '3':
                await ctx.author.send('**Not Yet Implemented**')
            else:
                await ctx.author.send('**ERROR** - Not a valid choice.')
            if content.find('!!') == -1:
                return await ctx.invoke(self.bot.get_command("me"), True)
            else:
                return
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
                embed = make_embed(icon=ctx.bot.user.avatar)
                embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                                 text="Aura - EVE Text RPG")
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
                    if ship_number >= 10:
                        stored_modules = '\n'.join(stored_ships_array)
                        embed.add_field(name="{} Module Hangar".format(region_name),
                                        value=stored_modules)
                        stored_ships_array = []
                if len(stored_ships_array) > 0:
                    stored_ships = '\n'.join(stored_ships_array)
                    embed.add_field(name="{} Ship Hangar".format(region_name),
                                    value=stored_ships)
                await ctx.author.send(embed=embed)

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.author.dm_channel

                msg = await self.bot.wait_for('message', check=check, timeout=120.0)
                content = msg.content
                module_array = list(set(ast.literal_eval('[{}]'.format(msg.content))))
                if type(module_array) is list and len(module_array) > 1:
                    sell_ships = []
                    sell_ships_text = []
                    total_isk = 0
                    count = 0
                    embed = make_embed(icon=self.bot.user.avatar)
                    embed.set_footer(icon_url=self.bot.user.avatar_url,
                                     text="Aura - EVE Text RPG")
                    for content in module_array:
                        for ship in ship_hangar[player[0][4]]:
                            if ship['selection'] == int(content):
                                sell_ships.append(ship['id'])
                                selected_ship = await game_functions.get_ship(int(ship['ship_type']))
                                total_isk += int(float(selected_ship['isk']) * 0.95)
                                sell_ships_text.append('{}'.format(selected_ship['name']))
                                count += 1
                                if count >= 10:
                                    count = 0
                                    stored_ships = '\n'.join(sell_ships_text)
                                    embed.add_field(name="Sell",
                                                    value="__**Sell**__\n{}".format(stored_ships), inline=False)
                                    sell_ships_text = []
                    if len(sell_ships_text) > 0:
                        stored_ships = '\n'.join(sell_ships_text)
                        embed.add_field(name="Sell",
                                        value="__**Sell**__\n{}".format(stored_ships), inline=False)
                    sale_price = '{0:,.2f}'.format(float(total_isk))
                    embed.add_field(name="Confirm Sale",
                                    value="For {} ISK \n\n"
                                          "**1.** Yes.\n"
                                          "**2.** No.\n".format(sale_price), inline=False)
                    await ctx.author.send(embed=embed)

                    def check(m):
                        return m.author == ctx.author and m.channel == ctx.author.dm_channel

                    msg = await self.bot.wait_for('message', check=check, timeout=120.0)
                    response = msg.content
                    if response != '1':
                        await ctx.author.send('**Sale Canceled**')
                        if content.find('!!') == -1:
                            return await ctx.invoke(self.bot.get_command("me"), True)
                        else:
                            return
                    else:
                        for sale in sell_ships:
                            for ship in ship_hangar[player[0][4]]:
                                if ship['id'] == sale:
                                    remove = ship
                                    ship_hangar[player[0][4]].remove(remove)
                                    break
                        new_hangar = ship_hangar
                        if new_hangar[player[0][4]] is None or len(new_hangar[player[0][4]]) < 1:
                            new_hangar.pop(player[0][4], None)
                            if len(new_hangar) == 0:
                                values = (None, int(player[0][5]) + total_isk, ctx.author.id,)
                            else:
                                values = (str(new_hangar), int(player[0][5]) + total_isk, ctx.author.id,)
                        else:
                            values = (str(new_hangar), int(player[0][5]) + total_isk, ctx.author.id,)
                        await self.update_journal(player[0], total_isk)
                        sql = ''' UPDATE eve_rpg_players
                                SET ship_hangar = (?),
                                    isk = (?)
                                WHERE
                                    player_id = (?); '''
                        await db.execute_sql(sql, values)
                        await ctx.author.send('**Sale Completed**')
                    return await ctx.invoke(self.bot.get_command("me"), True)
                if type(module_array) is list:
                    content = module_array[0]
                if int(content) in owned_ship_ids:
                    for ship in ship_hangar[player[0][4]]:
                        if ship['selection'] == int(content):
                            ship_id = ship['id']
                            selected_ship = await game_functions.get_ship(int(ship['ship_type']))
                            sale_price = ship['sale_price']
                            break
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
                    add_isk = int(float(selected_ship['isk'] * 0.95))
                    new_isk = player[0][5] + add_isk
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
                        values = (str(new_hangar), str(module_hangar), new_isk, ctx.author.id,)
                    if new_hangar[player[0][4]] is None or len(new_hangar[player[0][4]]) < 1:
                        new_hangar.pop(player[0][4], None)
                        if len(new_hangar) == 0:
                            values = (None, player[0][13], new_isk, ctx.author.id,)
                        else:
                            values = (str(new_hangar), player[0][13], new_isk, ctx.author.id,)
                    else:
                        values = (str(new_hangar), player[0][13], new_isk, ctx.author.id,)
                    await self.update_journal(player[0], add_isk)
                    sql = ''' UPDATE eve_rpg_players
                            SET ship_hangar = (?),
                                module_hangar = (?),
                                isk = (?)
                            WHERE
                                player_id = (?); '''
                    await db.execute_sql(sql, values)
                    await ctx.author.send('**Sold a {} for {} ISK**'.format(selected_ship['name'], sale_price))
                else:
                    await ctx.author.send('**ERROR** - Not a valid choice.')
                if content.find('!!') == -1:
                    return await ctx.invoke(self.bot.get_command("me"), True)
                else:
                    return
            elif content == '2':
                if player[0][13] is None:
                    embed = make_embed(icon=ctx.bot.user.avatar)
                    embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                                     text="Aura - EVE Text RPG")
                    embed.add_field(name="{} Module Hangar".format(region_name),
                                    value='No Modules Found In This Region')
                    return await ctx.author.send(embed=embed)
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
                module_count = 0
                embed = make_embed(icon=ctx.bot.user.avatar)
                embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                                 text="Aura - EVE Text RPG")
                for module in module_hangar[player[0][4]]:
                    sell_module_order[module_number] = int(module)
                    owned_module_ids.append(module_number)
                    module_info = await game_functions.get_module(int(module))
                    sale_price = '{0:,.2f}'.format(float(module_info['isk'] * 0.95))
                    stored_module_array.append(
                        '{}. {} *({} ISK)*'.format(module_number, module_info['name'], sale_price))
                    module_number += 1
                    module_count += 1
                    if module_count >= 10:
                        module_count = 0
                        stored_modules = '\n'.join(stored_module_array)
                        embed.add_field(name="{} Module Hangar".format(region_name),
                                        value=stored_modules)
                        stored_module_array = []
                if len(stored_module_array) > 0:
                    stored_modules = '\n'.join(stored_module_array)
                    embed.add_field(name="{} Module Hangar".format(region_name),
                                    value=stored_modules)
                await ctx.author.send(embed=embed)

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.author.dm_channel

                msg = await self.bot.wait_for('message', check=check, timeout=120.0)
                content = msg.content
                module_array = list(set(ast.literal_eval('[{}]'.format(msg.content))))
                if type(module_array) is list and len(module_array) > 1:
                    sell_modules_text = []
                    total_isk = 0
                    count = 0
                    embed = make_embed(icon=self.bot.user.avatar)
                    embed.set_footer(icon_url=self.bot.user.avatar_url,
                                     text="Aura - EVE Text RPG")
                    for modules in module_array:
                        module = sell_module_order[modules]
                        module_info = await game_functions.get_module(int(module))
                        total_isk += int(float(module_info['isk']) * 0.95)
                        sell_modules_text.append('{}'.format(module_info['name']))
                        count += 1
                        if count >= 10:
                            count = 0
                            stored_modules = '\n'.join(sell_modules_text)
                            embed.add_field(name="Sell",
                                            value="__**Sell**__\n{}".format(stored_modules), inline=False)
                            sell_modules_text = []
                    if len(sell_modules_text) > 0:
                        stored_modules = '\n'.join(sell_modules_text)
                        embed.add_field(name="Sell",
                                        value="__**Sell**__\n{}".format(stored_modules), inline=False)
                    sale_price = '{0:,.2f}'.format(float(total_isk))
                    embed.add_field(name="Confirm Sale",
                                    value="For {} ISK \n\n"
                                          "**1.** Yes.\n"
                                          "**2.** No.\n".format(sale_price), inline=False)
                    await ctx.author.send(embed=embed)

                    def check(m):
                        return m.author == ctx.author and m.channel == ctx.author.dm_channel

                    msg = await self.bot.wait_for('message', check=check, timeout=120.0)
                    response = msg.content
                    if response != '1':
                        await ctx.author.send('**Sale Canceled**')
                        if content.find('!!') == -1:
                            return await ctx.invoke(self.bot.get_command("me"), True)
                        else:
                            return
                    else:
                        module_hangar = ast.literal_eval(player[0][13])
                        for remove in module_array:
                            module_hangar[player[0][4]].remove(sell_module_order[remove])
                        if len(module_hangar[player[0][4]]) == 0:
                            module_hangar.pop(player[0][4], None)
                        if len(module_hangar) > 0:
                            hangar = str(module_hangar)
                        else:
                            hangar = None
                        await self.update_journal(player[0], total_isk)
                        sql = ''' UPDATE eve_rpg_players
                                SET module_hangar = (?),
                                    isk = (?)
                                WHERE
                                    player_id = (?); '''
                        values = (hangar, int(player[0][5]) + total_isk, ctx.author.id,)
                        await db.execute_sql(sql, values)
                        await ctx.author.send('**Sale Complete**')
                        return await ctx.invoke(self.bot.get_command("me"), True)
                if type(module_array) is list:
                    content = module_array[0]
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
                        await ctx.author.send('**Sale Canceled**')
                        if content.find('!!') == -1:
                            return await ctx.invoke(self.bot.get_command("me"), True)
                        else:
                            return
                    module_hangar[player[0][4]].remove(sell_module_order[int(content)])
                    new_hangar = module_hangar
                    add_isk = int(float(module_info['isk'] * 0.95))
                    new_isk = player[0][5] + add_isk
                    if new_hangar[player[0][4]] is None or len(new_hangar[player[0][4]]) < 1:
                        new_hangar.pop(player[0][4], None)
                        if len(new_hangar) == 0:
                            values = (None, new_isk, ctx.author.id,)
                        else:
                            values = (str(new_hangar), new_isk, ctx.author.id,)
                    else:
                        values = (str(new_hangar), new_isk, ctx.author.id,)
                    await self.update_journal(player[0], add_isk)
                    sql = ''' UPDATE eve_rpg_players
                            SET module_hangar = (?),
                                isk = (?)
                            WHERE
                                player_id = (?); '''
                    await db.execute_sql(sql, values)
                    await ctx.author.send('**Sold a {} for {} ISK**'.format(module_info['name'], sale_price))
                else:
                    await ctx.author.send('**ERROR** - Not a valid choice.')
                if content.find('!!') == -1:
                    return await ctx.invoke(self.bot.get_command("me"), True)
                else:
                    return
            elif content == '3':
                if player[0][19] is None or player[0][4] not in ast.literal_eval(player[0][19]):
                    embed = make_embed(icon=ctx.bot.user.avatar)
                    embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                                     text="Aura - EVE Text RPG")
                    embed.add_field(name="{} Component Hangar".format(region_name),
                                    value='No Components Found In This Region')
                    return await ctx.author.send(embed=embed)
                component_hangar = ast.literal_eval(player[0][19])
                stored_components_array = []
                owned_ship_ids = []
                component_number = 1
                component_count = 0
                embed = make_embed(icon=ctx.bot.user.avatar)
                for component in component_hangar[player[0][4]]:
                    component_count += 1
                    owned_ship_ids.append(component_number)
                    component['selection'] = component_number
                    component_info = await game_functions.get_component(int(component['type_id']))
                    sale_price = '{0:,.2f}'.format(float((component_info['isk'] * 0.95) * component['amount']))
                    component['sale_price'] = sale_price
                    stored_components_array.append('{}. {}x {} *({} ISK)*'.format(component_number, component['amount'],
                                                                                  component_info['name'], sale_price))
                    component_number += 1
                    if component_count >= 10:
                        component_count = 0
                        stored_components = '\n'.join(stored_components_array)
                        embed.add_field(name="{} Component Hangar".format(region_name),
                                        value=stored_components)
                        stored_components_array = []
                embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                                 text="Aura - EVE Text RPG")
                if len(stored_components_array) > 0:
                    stored_components = '\n'.join(stored_components_array)
                    embed.add_field(name="{} Component Hangar".format(region_name),
                                    value=stored_components)
                await ctx.author.send(embed=embed)

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.author.dm_channel

                msg = await self.bot.wait_for('message', check=check, timeout=120.0)
                content = msg.content
                module_array = list(set(ast.literal_eval('[{}]'.format(msg.content))))
                if type(module_array) is list and len(module_array) > 1:
                    sell_components = []
                    sell_components_text = []
                    total_isk = 0
                    count = 0
                    embed = make_embed(icon=self.bot.user.avatar)
                    embed.set_footer(icon_url=self.bot.user.avatar_url,
                                     text="Aura - EVE Text RPG")
                    for component in component_hangar[player[0][4]]:
                        for selling in module_array:
                            if component['selection'] == int(selling):
                                sell_components.append(component['id'])
                                selected_component = await game_functions.get_component(int(component['type_id']))
                                total_isk += int(float(selected_component['isk'] * component['amount']))
                                sell_components_text.append('{}x {}'.format(component['amount'],
                                                                            selected_component['name']))
                                count += 1
                                if count >= 10:
                                    count = 0
                                    stored_modules = '\n'.join(sell_components_text)
                                    embed.add_field(name="Sell",
                                                    value="__**Sell**__\n{}".format(stored_modules), inline=False)
                                    sell_components_text = []
                    if len(sell_components_text) > 0:
                        stored_modules = '\n'.join(sell_components_text)
                        embed.add_field(name="Sell",
                                        value="__**Sell**__\n{}".format(stored_modules), inline=False)
                    sale_price = '{0:,.2f}'.format(float(total_isk))
                    embed.add_field(name="Confirm Sale",
                                    value="For {} ISK \n\n"
                                          "**1.** Yes.\n"
                                          "**2.** No.\n".format(sale_price), inline=False)
                    await ctx.author.send(embed=embed)

                    def check(m):
                        return m.author == ctx.author and m.channel == ctx.author.dm_channel

                    msg = await self.bot.wait_for('message', check=check, timeout=120.0)
                    response = msg.content
                    if response != '1':
                        await ctx.author.send('**Sale Canceled**')
                        if content.find('!!') == -1:
                            return await ctx.invoke(self.bot.get_command("me"), True)
                        else:
                            return
                    else:
                        for sell_this in sell_components:
                            for component in component_hangar[player[0][4]]:
                                if component['id'] == sell_this:
                                    remove = component
                                    component_hangar[player[0][4]].remove(remove)
                        new_hangar = component_hangar
                        if new_hangar[player[0][4]] is None or len(new_hangar[player[0][4]]) < 1:
                            new_hangar.pop(player[0][4], None)
                            if len(new_hangar) == 0:
                                values = (None, int(player[0][5]) + total_isk, ctx.author.id,)
                            else:
                                values = (str(new_hangar), int(player[0][5]) + total_isk, ctx.author.id,)
                        else:
                            values = (str(new_hangar), int(player[0][5]) + total_isk, ctx.author.id,)
                        await self.update_journal(player[0], total_isk)
                        sql = ''' UPDATE eve_rpg_players
                                SET component_hangar = (?),
                                    isk = (?)
                                WHERE
                                    player_id = (?); '''
                        await db.execute_sql(sql, values)
                        await ctx.author.send('**Sale Completed**')
                    return await ctx.invoke(self.bot.get_command("me"), True)
                if type(module_array) is list:
                    content = module_array[0]
                if int(content) in owned_ship_ids:
                    for component in component_hangar[player[0][4]]:
                        if component['selection'] == int(content):
                            component_id = component['id']
                            selected_component = await game_functions.get_component(int(component['type_id']))
                            sale_price = component['sale_price']
                            break
                    embed = make_embed(icon=self.bot.user.avatar)
                    embed.set_footer(icon_url=self.bot.user.avatar_url,
                                     text="Aura - EVE Text RPG")
                    embed.set_thumbnail(url="{}".format(selected_component['image']))
                    embed.add_field(name="Confirm Sale",
                                    value="Are you sure you want to sell **{}x {}** for {} ISK\n\n"
                                          "**1.** Yes.\n"
                                          "**2.** No.\n".format(component['amount'], selected_component['name'],
                                                                sale_price))
                    await ctx.author.send(embed=embed)

                    def check(m):
                        return m.author == ctx.author and m.channel == ctx.author.dm_channel

                    msg = await self.bot.wait_for('message', check=check, timeout=120.0)
                    content = msg.content
                    if content != '1':
                        return await ctx.author.send('**Sale Canceled**')
                    for component in component_hangar[player[0][4]]:
                        if component['id'] == component_id:
                            remove = component
                            break
                    component_hangar[player[0][4]].remove(remove)
                    new_hangar = component_hangar
                    add_isk = int(float(component_info['isk'] * 0.95))
                    new_isk = player[0][5] + add_isk
                    await self.update_journal(player[0], add_isk)
                    if new_hangar[player[0][4]] is None or len(new_hangar[player[0][4]]) < 1:
                        new_hangar.pop(player[0][4], None)
                        if len(new_hangar) == 0:
                            values = (None, new_isk, ctx.author.id,)
                        else:
                            values = (str(new_hangar), new_isk, ctx.author.id,)
                    else:
                        values = (str(new_hangar), new_isk, ctx.author.id,)
                    sql = ''' UPDATE eve_rpg_players
                            SET component_hangar = (?),
                                isk = (?)
                            WHERE
                                player_id = (?); '''
                    await db.execute_sql(sql, values)
                    await ctx.author.send('**Sold {} {} for {} ISK**'.format(component['amount'],
                                                                             selected_component['name'],
                                                                             sale_price))
                elif '!!' not in content:
                    await ctx.author.send('**ERROR** - Not a valid choice.')
            elif '!!' not in content:
                await ctx.author.send('**ERROR** - Not a valid choice.')
        elif '!!' not in content:
            await ctx.author.send('**ERROR** - Not a valid choice.')
        if content.find('!!') == -1:
            return await ctx.invoke(self.bot.get_command("me"), True)
        else:
            return

    async def update_journal(self, player, isk):
        entry = 'Market Transaction'
        player = await game_functions.refresh_player(player)
        if player[20] is not None:
            journal = ast.literal_eval(player[20])
            if len(journal) == 10:
                journal.pop(0)
            transaction = {'isk': isk, 'type': entry}
            journal.append(transaction)
        else:
            transaction = {'isk': isk, 'type': entry}
            journal = [transaction]
        sql = ''' UPDATE eve_rpg_players
                SET wallet_journal = (?)
                WHERE
                    player_id = (?); '''
        values = (str(journal), player[2],)
        return await db.execute_sql(sql, values)
