import ast

from discord.ext import commands

from aura.core import checks
from aura.lib import db
from aura.lib import game_assets
from aura.lib import game_functions
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
        wallet_balance = '{0:,.2f}'.format(float(player[0][5]))
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
                              "**5.** Visit the regional market.\n"
                              "**6.** View your asset list.\n".format(
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
        elif content == '6':
            await self.asset_list(ctx)
        else:
            return await ctx.author.send('**ERROR** - Not a valid choice.')

    async def change_task(self, ctx, player):
        if player[0][6] == 20:
            return await ctx.author.send('**ERROR** - You need to finish traveling first.')
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
                                  "**5.** Join a fleet.\n"
                                  "**PVE Tasks**\n"
                                  "**6.** Kill belt rats.\n"
                                  "**7.** Run anomalies in the system.\n"
                                  "**8.** Do some exploration and run sites in the system.\n"
                                  "**Mining Tasks**\n"
                                  "**9.** Mine an asteroid belt.\n"
                                  "**10.** Mine a mining anomaly.\n".format(current_task))
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
                                  "**Mining Tasks**\n"
                                  "**9.** Mine an asteroid belt.\n".format(current_task))
            accepted = [1, 4, 6, 8, 9]
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120.0)
        content = msg.content
        if content == '5' or content == '8' or content == '10':
            return await ctx.author.send('**Not Yet Implemented**')
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
        if int(content) in region_connections:
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
        """Fit your current ship."""
        if ctx.guild is not None:
            await ctx.message.delete()
        sql = ''' SELECT * FROM eve_rpg_players WHERE `player_id` = (?) '''
        values = (ctx.message.author.id,)
        player = await db.select_var(sql, values)
        if player[0][6] is not 1:
            return await ctx.author.send('**ERROR** - You must be docked to do this.')
        region_id = int(player[0][4])
        region_name = await game_functions.get_region(region_id)
        ship = await game_functions.get_ship(int(player[0][14]))
        module_count = 0
        clean_equipped_modules = ''
        remove_module_order = {}
        module_number = 1
        remove_commands = []
        if player[0][12] is not None:
            equipped_modules = ast.literal_eval(player[0][12])
            module_count = len(equipped_modules)
            equipped_modules_array = []
            for item in equipped_modules:
                remove_module_order[module_number] = int(item)
                module = await game_functions.get_module(int(item))
                module_attack = module['attack']
                module_defense = module['defense']
                module_maneuver = module['maneuver']
                module_tracking = module['tracking']
                stats = '({}%/{}%/{}%/{}%)'.format(module_attack * 100, module_defense * 100,
                                                   module_maneuver * 100, module_tracking * 100)
                if module['special'] is not None:
                    stats = '{} {}'.format(stats, module['special'])
                equipped_modules_array.append('**{}.** {} - {}'.format(module_number, module['name'], stats))
                remove_commands.append(module_number)
                module_number += 1
            clean_equipped_modules = '\n'.join(equipped_modules_array)
        ship_attack, ship_defense, ship_maneuver, ship_tracking = \
            await game_functions.get_combat_attributes(player[0], int(player[0][14]))
        value = '**{}** - {}/{} Module Slots\n\n**Current Attack:** {}\n**Current Defense:** {}\n**Current Maneuver:** {}\n' \
                '**Current Tracking:** {}'.format(ship['name'], module_count, ship['slots'], ship_attack, ship_defense,
                                                  ship_maneuver, ship_tracking)
        if player[0][12] is not None:
            value = '{}\n\n__Equipped Modules__\n{}'.format(value, clean_equipped_modules)
        embed = make_embed(icon=ctx.bot.user.avatar)
        ship_image = await game_functions.get_ship_image(int(player[0][14]))
        embed.set_thumbnail(url="{}".format(ship_image))
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Ship Fitting".format(region_name),
                        value=value, inline=False)
        equip_module_order = {}
        equip_commands = []
        if player[0][13] is not None:
            module_hangar = ast.literal_eval(player[0][13])
            if player[0][4] in module_hangar:
                stored_modules_array = []
                for item in module_hangar[player[0][4]]:
                    equip_module_order[module_number] = int(item)
                    module = await game_functions.get_module(int(item))
                    module_attack = module['attack']
                    module_defense = module['defense']
                    module_maneuver = module['maneuver']
                    module_tracking = module['tracking']
                    stats = '({}%/{}%/{}%/{}%)'.format(module_attack * 100, module_defense * 100,
                                                       module_maneuver * 100, module_tracking * 100)
                    if module['special'] is not None:
                        stats = '{} {}'.format(stats, module['special'])
                    stored_modules_array.append('**{}.** {} - {}'.format(module_number, module['name'], stats))
                    equip_commands.append(module_number)
                    module_number += 1
                stored_modules = '\n'.join(stored_modules_array)
                embed.add_field(name="Module Hangar",
                                value='{}'.format(stored_modules), inline=False)
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120.0)
        content = int(msg.content)
        if int(msg.content) in remove_commands:
            selected_module = await game_functions.get_module(int(remove_module_order[content]))
            embed = make_embed(icon=self.bot.user.avatar)
            embed.set_footer(icon_url=self.bot.user.avatar_url,
                             text="Aura - EVE Text RPG")
            embed.set_thumbnail(url="{}".format(selected_module['image']))
            embed.add_field(name="Confirm Switch",
                            value="Are you sure you want to remove a **{}**\n\n"
                                  "**1.** Yes.\n"
                                  "**2.** No.\n".format(selected_module['name']))
            await ctx.author.send(embed=embed)

            def check(m):
                return m.author == ctx.author and m.channel == ctx.author.dm_channel

            msg = await self.bot.wait_for('message', check=check, timeout=120.0)
            response = msg.content
            if response != '1':
                return await ctx.author.send('**Removal Canceled**')
            if player[0][13] is not None and player[0][4] in ast.literal_eval(player[0][13]):
                module_hangar = ast.literal_eval(player[0][13])
                module_hangar[player[0][4]].append(remove_module_order[content])
            elif player[0][13] is not None:
                module_hangar = ast.literal_eval(player[0][13])
                module_hangar[player[0][4]] = [remove_module_order[content]]
            else:
                module_hangar = {player[0][4]: [remove_module_order[content]]}
            sql = ''' UPDATE eve_rpg_players
                    SET modules = (?),
                        module_hangar = (?)
                    WHERE
                        player_id = (?); '''
            remove_module_order.pop(content, None)
            if remove_module_order is not None and len(remove_module_order) > 0:
                now_equipped = []
                for key, module in remove_module_order.items():
                    now_equipped.append(module)
                values = (str(now_equipped), str(module_hangar), ctx.author.id,)
            else:
                values = (None, str(module_hangar), ctx.author.id,)
            await db.execute_sql(sql, values)
            return await ctx.author.send('**{} Has Been Removed**'.format(selected_module['name']))
        elif int(msg.content) in equip_commands:
            if module_count >= ship['slots']:
                return await ctx.author.send('**All module slots are occupied for this ship**')
            selected_module = await game_functions.get_module(int(equip_module_order[content]))
            embed = make_embed(icon=self.bot.user.avatar)
            embed.set_footer(icon_url=self.bot.user.avatar_url,
                             text="Aura - EVE Text RPG")
            embed.set_thumbnail(url="{}".format(selected_module['image']))
            embed.add_field(name="Confirm Switch",
                            value="Are you sure you want to equip a **{}**\n\n"
                                  "**1.** Yes.\n"
                                  "**2.** No.\n".format(selected_module['name']))
            await ctx.author.send(embed=embed)

            def check(m):
                return m.author == ctx.author and m.channel == ctx.author.dm_channel

            msg = await self.bot.wait_for('message', check=check, timeout=120.0)
            response = msg.content
            if player[0][12] is not None:
                equipped_modules = ast.literal_eval(player[0][12])
                equipped_modules.append(equip_module_order[content])
            else:
                equipped_modules = [equip_module_order[content]]
            if response != '1':
                return await ctx.author.send('**Equipping Module Canceled**')
            module_hangar = ast.literal_eval(player[0][13])
            module_hangar[player[0][4]].remove(equip_module_order[content])
            sql = ''' UPDATE eve_rpg_players
                    SET modules = (?),
                        module_hangar = (?)
                    WHERE
                        player_id = (?); '''
            if module_hangar[player[0][4]] is None or len(module_hangar[player[0][4]]) < 1:
                module_hangar.pop(player[0][4], None)
                if len(module_hangar) == 0:
                    values = (str(equipped_modules), None, ctx.author.id,)
                else:
                    values = (str(equipped_modules), module_hangar, ctx.author.id,)
            else:
                values = (str(equipped_modules), str(module_hangar), ctx.author.id,)
            await db.execute_sql(sql, values)
            return await ctx.author.send('**{} Has Been Equipped**'.format(selected_module['name']))
        else:
            return await ctx.author.send('**ERROR** - Not a valid choice.')

    async def change_ship(self, ctx):
        if ctx.guild is not None:
            await ctx.message.delete()
        sql = ''' SELECT * FROM eve_rpg_players WHERE `player_id` = (?) '''
        values = (ctx.message.author.id,)
        player = await db.select_var(sql, values)
        if player[0][6] is not 1:
            return await ctx.author.send('**ERROR** - You must be docked to do this.')
        region_id = int(player[0][4])
        region_name = await game_functions.get_region(region_id)
        current_ship = await game_functions.get_ship_name(int(player[0][14]))
        if player[0][15] is None:
            embed = make_embed(icon=ctx.bot.user.avatar)
            embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                             text="Aura - EVE Text RPG")
            embed.add_field(name="{} Ship Hangar".format(region_name),
                            value='No Ships Found In This Region')
            return await ctx.author.send(embed=embed)
        else:
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
            for ship in ship_hangar[player[0][4]]:
                owned_ship_ids.append(int(ship))
                ship_name = await game_functions.get_ship_name(int(ship))
                stored_ships_array.append('{}. {}'.format(ship, ship_name))
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
                selected_ship = await game_functions.get_ship(int(content))
                embed = make_embed(icon=self.bot.user.avatar)
                embed.set_footer(icon_url=self.bot.user.avatar_url,
                                 text="Aura - EVE Text RPG")
                embed.set_thumbnail(url="{}".format(selected_ship['image']))
                embed.add_field(name="Confirm Switch",
                                value="Are you sure you want to switch from a **{}** into a **{}**\n\n"
                                      "**1.** Yes.\n"
                                      "**2.** No.\n".format(current_ship, selected_ship['name']))
                await ctx.author.send(embed=embed)

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.author.dm_channel

                msg = await self.bot.wait_for('message', check=check, timeout=120.0)
                content = msg.content
                if content != '1':
                    return await ctx.author.send('**Switch Canceled**')
                new_hangar = ship_hangar[player[0][4]].remove(selected_ship['id'])
                if new_hangar is None:
                    new_hangar = {player[0][4]: [int(player[0][14])]}
                else:
                    new_hangar[player[0][4]].append(int(player[0][14]))
                sql = ''' UPDATE eve_rpg_players
                        SET ship = (?),
                            ship_hangar = (?)
                        WHERE
                            player_id = (?); '''
                values = (int(selected_ship['id']), str(new_hangar), ctx.author.id,)
                await db.execute_sql(sql, values)
                return await ctx.author.send('**A {} Is Now Your Active Ship**'.format(selected_ship['name']))
            else:
                return await ctx.author.send('**ERROR** - Not a valid choice.')

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
                content = msg.content
                current_hangar = ast.literal_eval(player[0][15])
                if content != '1':
                    return await ctx.author.send('**Purchase Canceled**')
                if current_hangar is None:
                    current_hangar = {player[0][4]: [ship['id']]}
                elif player[0][4] not in current_hangar:
                    current_hangar[player[0][4]] = [ship['id']]
                else:
                    current_hangar[player[0][4]].append(ship['id'])
                sql = ''' UPDATE eve_rpg_players
                        SET ship_hangar = (?),
                            isk = (?)
                        WHERE
                            player_id = (?); '''
                remaining_isk = int(player[0][5]) - int(ship['isk'])
                values = (str(current_hangar), remaining_isk, ctx.author.id,)
                await db.execute_sql(sql, values)
                return await ctx.author.send('**{} Purchase Complete, It Is Now Stored In Your Ship Hangar For This '
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
                return await ctx.author.send('**{} Purchase Complete, It Is Now Stored In Your Module Hangar For This '
                                             'Region**'.format(module['name']))
            return await ctx.author.send('**ERROR** - Not a valid choice.')
        elif content == '3':
            return await ctx.author.send('**Not Yet Implemented**')
        else:
            return await ctx.author.send('**ERROR** - Not a valid choice.')

    async def asset_list(self, ctx):
        """View your assets."""
        if ctx.guild is not None:
            await ctx.message.delete()
        sql = ''' SELECT * FROM eve_rpg_players WHERE `player_id` = (?) '''
        values = (ctx.message.author.id,)
        player = await db.select_var(sql, values)
        if player[0][15] is None and player[0][13] is None:
            embed = make_embed(icon=ctx.bot.user.avatar)
            embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                             text="Aura - EVE Text RPG")
            embed.add_field(name="Asset List",
                            value='No Assets Found')
            return await ctx.author.send(embed=embed)
        else:
            embed = make_embed(icon=ctx.bot.user.avatar)
            embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                             text="Aura - EVE Text RPG")
            if player[0][15] is not None:
                ship_hangar = ast.literal_eval(player[0][15])
                stored_ships_array = []
                for key, ships in ship_hangar.items():
                    for ship in ships:
                        region_name = await game_functions.get_region(key)
                        ship_name = await game_functions.get_ship_name(int(ship))
                        stored_ships_array.append('{} - {}'.format(ship_name, region_name))
                stored_ships = '\n'.join(stored_ships_array)
                embed.add_field(name="Ships",
                                value='{}'.format(stored_ships))
            if player[0][13] is not None:
                module_hangar = ast.literal_eval(player[0][13])
                stored_modules_array = []
                for key, items in module_hangar.items():
                    for item in items:
                        region_name = await game_functions.get_region(key)
                        module_name = await game_functions.get_module_name(int(item))
                        stored_modules_array.append('{} - {}'.format(module_name, region_name))
                stored_modules = '\n'.join(stored_modules_array)
                embed.add_field(name="Modules",
                                value='{}'.format(stored_modules))
            await ctx.author.send(embed=embed)
