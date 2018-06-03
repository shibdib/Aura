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
            await ctx.message.delete()
        sql = ''' SELECT * FROM eve_rpg_players WHERE `player_id` = (?) '''
        values = (ctx.message.author.id,)
        player = await db.select_var(sql, values)
        if player[0][6] is not 1:
            return await ctx.author.send('**ERROR** - You must be docked to do this.')
        region_id = int(player[0][4])
        region_name = await game_functions.get_region(region_id)
        player_ship_obj = ast.literal_eval(player[0][14])
        ship = await game_functions.get_ship(int(player_ship_obj['ship_type']))
        module_count = 0
        clean_equipped_modules = ''
        remove_module_order = {}
        module_number = 1
        remove_commands = []
        #  check if insured
        insured = ''
        if 'insured' in player_ship_obj:
            insured = '\n*This Ship Is Insured*'
        #  check if killmark
        killmarks = ''
        if 'kill_marks' in player_ship_obj:
            killmarks = '\n**{} Kill Marks**'
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
            await game_functions.get_combat_attributes(player[0], int(player_ship_obj['ship_type']))
        value = '**{}** - {}/{} Module Slots{}{}\n\n**Current Attack:** {}\n**Current Defense:** {}\n**Current Maneuver:** {}\n' \
                '**Current Tracking:** {}'.format(ship['name'], module_count, ship['slots'], killmarks, insured,
                                                  ship_attack, ship_defense, ship_maneuver, ship_tracking)
        if player[0][12] is not None:
            value = '{}\n\n__Equipped Modules__\n{}'.format(value, clean_equipped_modules)
        embed = make_embed(icon=ctx.bot.user.avatar)
        ship_image = await game_functions.get_ship_image(int(player_ship_obj['ship_type']))
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
        if len(msg.content) > 1:
            module_array = ast.literal_eval('[{}]'.format(msg.content))
            if module_array is list:
                equip_modules = []
                equip_modules_text = []
                remove_modules = []
                remove_modules_text = []
                for module in module_array:
                    if int(module) in remove_commands:
                        selected_module = await game_functions.get_module(int(remove_module_order[module]))
                        remove_modules_text.append('{}'.format(selected_module['name']))
                        remove_modules.append(int(remove_module_order[module]))
                    elif int(module) in equip_commands:
                        selected_module = await game_functions.get_module(int(equip_module_order[module]))
                        equip_modules_text.append('{}'.format(selected_module['name']))
                        equip_modules.append(int(equip_module_order[module]))
                if (module_count + len(equip_modules)) - len(remove_modules) >= ship['slots']:
                    return await ctx.author.send('**The current selection would put you over the maximum modules for '
                                                 'this ship**')
                equip_list = '\n'.join(equip_modules_text)
                remove_list = '\n'.join(remove_modules_text)
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
                    return await ctx.author.send('**Changes Canceled**')
                if len(remove_modules) > 0:
                    if player[0][13] is not None and player[0][4] in ast.literal_eval(player[0][13]):
                        module_hangar = ast.literal_eval(player[0][13])
                        module_hangar[player[0][4]].join(remove_modules)
                    elif player[0][13] is not None:
                        module_hangar = ast.literal_eval(player[0][13])
                        module_hangar[player[0][4]] = remove_modules
                    else:
                        module_hangar = {player[0][4]: remove_modules}
                    equipped_modules = ast.literal_eval(player[0][12])
                    for remove in remove_modules:
                        equipped_modules.remove(remove)
                    player[0][13] = str(module_hangar)
                    if len(equipped_modules) > 0:
                        player[0][12] = str(equipped_modules)
                    else:
                        player[0][12] = None
                if len(equip_modules) > 0:
                    if player[0][12] is not None:
                        equipped_modules = ast.literal_eval(player[0][12])
                        equipped_modules.join(equip_modules)
                    else:
                        equipped_modules = equip_modules
                    module_hangar = ast.literal_eval(player[0][13])
                    for remove in equip_modules:
                        module_hangar[player[0][4]].remove(remove)
                    player[0][13] = str(module_hangar)
                    player[0][12] = str(equipped_modules)
                sql = ''' UPDATE eve_rpg_players
                        SET modules = (?),
                            module_hangar = (?)
                        WHERE
                            player_id = (?); '''
                values = (player[0][12], player[0][13], ctx.author.id,)
                await db.execute_sql(sql, values)
                return await ctx.author.send('**Changes Complete**')
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
                        values = (str(equipped_modules), str(module_hangar), ctx.author.id,)
                else:
                    values = (str(equipped_modules), str(module_hangar), ctx.author.id,)
                await db.execute_sql(sql, values)
                return await ctx.author.send('**{} Has Been Equipped**'.format(selected_module['name']))
            else:
                return await ctx.author.send('**ERROR** - Not a valid choice.')
