import ast

from discord.ext import commands

from aura.core import checks
from aura.lib import db
from aura.lib import game_functions
from aura.utils import make_embed


class ShipFitting:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session
        self.config = bot.config
        self.logger = bot.logger

    @commands.command(name='fitting', case_insensitive=True)
    @checks.spam_check()
    @checks.is_whitelist()
    @checks.has_account()
    async def ship_fitting(self, ctx):
        """Fit your current ship."""
        if ctx.guild is not None:
            try:
                await ctx.message.delete()
            except Exception:
                pass
        sql = ''' SELECT * FROM eve_rpg_players WHERE `player_id` = (?) '''
        values = (ctx.message.author.id,)
        player = await db.select_var(sql, values)
        if player[0][6] is not 1:
            await ctx.author.send('**ERROR** - You must be docked to do this.')
            return await ctx.invoke(self.bot.get_command("me"), True)
        region_id = int(player[0][4])
        region_name = await game_functions.get_region(region_id)
        player_ship_obj = ast.literal_eval(player[0][14])
        ship = await game_functions.get_ship(int(player_ship_obj['ship_type']))
        drone_size = 0
        clean_equipped_modules = ''
        clean_equipped_drones = ''
        remove_module_order = {}
        module_number = 1
        remove_commands = []
        remove_drones_commands = []
        #  check if insured
        insured = ''
        if 'insured' in player_ship_obj:
            insured = '\n*This Ship Is Insured*'
        #  check if killmark
        killmarks = ''
        if 'kill_marks' in player_ship_obj:
            killmarks = '\n**{} Kill Marks**'
        module_count = 0
        drone_count = 0
        if player[0][12] is not None:
            equipped_modules = ast.literal_eval(player[0][12])
            equipped_modules_array = []
            equipped_drones_array = []
            for item in equipped_modules:
                module = await game_functions.get_module(int(item))
                if module['class'] > 9:
                    drone_size += module['size']
                    remove_module_order[module_number] = int(item)
                    drone_attack = module['attack']
                    drone_defense = module['defense']
                    drone_maneuver = module['maneuver']
                    drone_tracking = module['tracking']
                    stats = '({}/{}/{}/{})'.format(drone_attack, drone_defense,
                                                   drone_maneuver, drone_tracking)
                    if module['special'] is not None:
                        stats = '{} {}'.format(stats, module['special'])
                    equipped_drones_array.append('**{}.** {} - {}'.format(module_number, module['name'], stats))
                    remove_drones_commands.append(module_number)
                    module_number += 1
                    drone_count += 1
                else:
                    module_count += 1
                    remove_module_order[module_number] = int(item)
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
            clean_equipped_drones = '\n'.join(equipped_drones_array)
        ship_attack, ship_defense, ship_maneuver, ship_tracking = \
            await game_functions.get_combat_attributes(player[0], int(player_ship_obj['ship_type']))
        value = '**{}** - {}/{} Module Slots{}{}\n\n**Current Attack:** {}\n**Current Defense:** {}\n**Current Maneuver:** {}\n**Current Tracking:** {}'.format(ship['name'], module_count, ship['slots'], killmarks, insured, ship_attack, ship_defense, ship_maneuver, ship_tracking)
        if player[0][12] is not None:
            value = '{}\n\n__Equipped Modules__\n{}'.format(value, clean_equipped_modules)
        if len(remove_drones_commands) > 0:
            value = '{}\n\n**{}m3/{}m3 Drone Bay**\n__Equipped Drones__\n{}'.format(value, drone_size, ship['drone_bay'],
                                                                                    clean_equipped_drones)
        embed = make_embed(icon=ctx.bot.user.avatar)
        ship_image = await game_functions.get_ship_image(int(player_ship_obj['ship_type']))
        embed.set_thumbnail(url="{}".format(ship_image))
        embed.set_footer(icon_url=ctx.bot.user.avatar_url, text="Aura - EVE Text RPG")
        embed.add_field(name="Ship Fitting".format(region_name), value=value, inline=False)
        equip_module_order = {}
        equip_commands = []
        equip_drones_commands = []
        if player[0][13] is not None:
            module_hangar = ast.literal_eval(player[0][13])
            if player[0][4] in module_hangar:
                stored_modules_array = []
                for item in module_hangar[player[0][4]]:
                    module = await game_functions.get_module(int(item))
                    if module['class'] > 9 and ship['drone_bay'] == 0:
                        continue
                    equip_module_order[module_number] = int(item)
                    module_attack = module['attack']
                    module_defense = module['defense']
                    module_maneuver = module['maneuver']
                    module_tracking = module['tracking']
                    stats = '({}%/{}%/{}%/{}%)'.format(module_attack * 100, module_defense * 100,
                                                       module_maneuver * 100, module_tracking * 100)
                    if module['class'] > 9 and ship['drone_bay'] > 0:
                        stats = '({}/{}/{}/{}) - Size: {}m3'.format(module_attack, module_defense,
                                                                    module_maneuver, module_tracking, module['size'])
                        equip_drones_commands.append(module_number)
                    else:
                        equip_commands.append(module_number)
                    if module['special'] is not None:
                        stats = '{} {}'.format(stats, module['special'])
                    stored_modules_array.append('**{}.** {} - {}'.format(module_number, module['name'], stats))
                    module_number += 1
                if len(stored_modules_array) > 0:
                    stored_modules = '\n'.join(stored_modules_array)
                    embed.add_field(name="Module/Drone Hangar", value='{}'.format(stored_modules), inline=False)
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120.0)
        module_array = ast.literal_eval('[{}]'.format(msg.content))
        if type(module_array) is list:
            equip_modules = []
            equip_modules_text = []
            remove_modules = []
            remove_modules_text = []
            equip_size = 0
            equip_drones_text = []
            remove_size = 0
            remove_drones_text = []
            drone_equip_count = 0
            drone_remove_count = 0
            for module in module_array:
                if int(module) in remove_commands:
                    selected_module = await game_functions.get_module(int(remove_module_order[module]))
                    remove_modules_text.append('{}'.format(selected_module['name']))
                    remove_modules.append(int(remove_module_order[module]))
                elif int(module) in equip_commands:
                    selected_module = await game_functions.get_module(int(equip_module_order[module]))
                    equip_modules_text.append('{}'.format(selected_module['name']))
                    equip_modules.append(int(equip_module_order[module]))
                elif int(module) in equip_drones_commands:
                    selected_module = await game_functions.get_module(int(equip_module_order[module]))
                    equip_size += selected_module['size']
                    equip_drones_text.append('{}'.format(selected_module['name']))
                    equip_modules.append(int(equip_module_order[module]))
                    drone_equip_count += 1
                elif int(module) in remove_drones_commands:
                    selected_module = await game_functions.get_module(int(equip_module_order[module]))
                    remove_size += selected_module['size']
                    remove_drones_text.append('{}'.format(selected_module['name']))
                    remove_modules.append(int(equip_module_order[module]))
                    drone_remove_count += 1
            if ((int(drone_size) + int(equip_size)) - int(remove_size)) > ship['drone_bay']:
                await ctx.author.send('**The current selection would overfill your drone bay**')
                return await ctx.invoke(self.bot.get_command("me"), True)
            if ((int(module_count) + (len(equip_modules) - drone_equip_count)) - (len(remove_modules) -
                                                                                  drone_remove_count)) > ship['slots']:
                await ctx.author.send('**The current selection would put you over the maximum modules for this '
                                      'ship**')
                return await ctx.invoke(self.bot.get_command("me"), True)
            equip_list = '\n'.join(equip_modules_text)
            if len(equip_drones_commands) > 0:
                equip_list = equip_list + '\n'.join(equip_drones_text)
            remove_list = '\n'.join(remove_modules_text)
            if len(remove_drones_commands) > 0:
                remove_list = remove_list + '\n'.join(remove_drones_text)
            embed = make_embed(icon=self.bot.user.avatar)
            embed.set_footer(icon_url=self.bot.user.avatar_url,
                             text="Aura - EVE Text RPG")
            embed.add_field(name="Confirm Switch",
                            value="__Remove__\n{}\n__Equip__\n{}\n\n"
                                  "**1.** Yes.\n"
                                  "**2.** No.\n".format(remove_list, equip_list))
            await ctx.author.send(embed=embed)

            def check(m):
                return m.author == ctx.author and m.channel == ctx.author.dm_channel

            msg = await self.bot.wait_for('message', check=check, timeout=120.0)
            response = msg.content
            if response != '1':
                await ctx.author.send('**Changes Canceled**')
                return await ctx.invoke(self.bot.get_command("me"), True)
            hangar = None
            equipped = None
            if len(remove_modules) > 0:
                if player[0][13] is not None and player[0][4] in ast.literal_eval(player[0][13]):
                    module_hangar = ast.literal_eval(player[0][13])
                    module_hangar[player[0][4]] += remove_modules
                elif player[0][13] is not None:
                    module_hangar = ast.literal_eval(player[0][13])
                    module_hangar[player[0][4]] = remove_modules
                else:
                    module_hangar = {player[0][4]: remove_modules}
                equipped_modules = ast.literal_eval(player[0][12])
                for remove in remove_modules:
                    equipped_modules.remove(remove)
                if len(equipped_modules) > 0:
                    equipped = str(equipped_modules)
                else:
                    equipped = []
                hangar = str(module_hangar)
            if hangar is None:
                hangar = player[0][13]
            if equipped is None:
                equipped = player[0][12]
            if len(equip_modules) > 0:
                if equipped is not None and type(equipped) is str:
                    equipped_modules = ast.literal_eval(equipped)
                    equipped_modules += equip_modules
                else:
                    equipped_modules = equip_modules
                module_hangar = ast.literal_eval(hangar)
                for remove in equip_modules:
                    module_hangar[player[0][4]].remove(remove)
            if len(module_hangar[player[0][4]]) == 0:
                module_hangar.pop(player[0][4], None)
            if len(module_hangar) > 0:
                hangar = str(module_hangar)
            else:
                hangar = None
            if len(equipped_modules) > 0:
                equipped = str(equipped_modules)
            else:
                equipped = None
            sql = ''' UPDATE eve_rpg_players
                    SET modules = (?),
                        module_hangar = (?)
                    WHERE
                        player_id = (?); '''
            values = (equipped, hangar, ctx.author.id,)
            await db.execute_sql(sql, values)
            await ctx.author.send('**Changes Complete**')
            return await ctx.invoke(self.bot.get_command("me"), True)
        else:
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
                    await ctx.author.send('**Removal Canceled**')
                    return await ctx.invoke(self.bot.get_command("me"), True)
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
                await ctx.author.send('**{} Has Been Removed**'.format(selected_module['name']))
                return await ctx.invoke(self.bot.get_command("me"), True)
            elif int(msg.content) in equip_commands:
                if module_count >= ship['slots']:
                    await ctx.author.send('**All module slots are occupied for this ship**')
                    return await ctx.invoke(self.bot.get_command("me"), True)
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
                    await ctx.author.send('**Equipping Module Canceled**')
                    return await ctx.invoke(self.bot.get_command("me"), True)
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
                        values = (str(equipped_modules), str(module_hangar), ctx.author.id,)
                else:
                    values = (str(equipped_modules), str(module_hangar), ctx.author.id,)
                await db.execute_sql(sql, values)
                await ctx.author.send('**{} Has Been Equipped**'.format(selected_module['name']))
            else:
                await ctx.author.send('**ERROR** - Not a valid choice.')
            return await ctx.invoke(self.bot.get_command("me"), True)
