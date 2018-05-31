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
        ship = await game_functions.get_ship(int(player[0][14]))
        module_count = 0
        clean_equipped_modules = ''
        if player[0][12] is not None:
            equipped_modules = ast.literal_eval(player[0][12])
            module_count = len(equipped_modules)
            equipped_modules_array = []
            for item in equipped_modules:
                module = await game_functions.get_module(int(item))
                module_attack = module['attack']
                module_defense = module['defense']
                module_maneuver = module['maneuver']
                module_tracking = module['tracking']
                stats = '({}/{}/{}/{})'.format(module_attack, module_defense, module_maneuver, module_tracking)
                if module['special'] is not None:
                    stats = '{} {}'.format(stats, module['special'])
                    equipped_modules_array.append('{} - {}'.format(module['name'], stats))
            clean_equipped_modules = '\n'.join(equipped_modules_array)
        ship_attack, ship_defense, ship_maneuver, ship_tracking = \
            await game_functions.get_combat_attributes(int(player[0][14]))
        value = '{} - {}/{} Module Slots\nCurrent Attack: {}\nCurrent Defense: {}\nCurrent Maneuver: {}\n' \
                'Current Tracking: {}'.format(ship['name'], module_count, ship['slots'], ship_attack, ship_defense,
                                              ship_maneuver, ship_tracking)
        if player[0][12] is not None:
            value = '{}\n\n__Equipped Modules__{}'.format(value, clean_equipped_modules)
        embed = make_embed(icon=ctx.bot.user.avatar)
        ship_image = await game_functions.get_ship_image(int(player[0][14]))
        embed.set_thumbnail(url="{}".format(ship_image))
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Ship Fitting".format(region_name),
                        value=value)
        if player[0][13] is not None:
            module_hangar = ast.literal_eval(player[0][13])
            if player[0][4] in module_hangar:
                stored_modules_array = []
                for item in module_hangar[player[0][4]]:
                    module = await game_functions.get_module(int(item))
                    module_attack = module['attack']
                    module_defense = module['defense']
                    module_maneuver = module['maneuver']
                    module_tracking = module['tracking']
                    stats = '({}/{}/{}/{})'.format(module_attack, module_defense, module_maneuver, module_tracking)
                    if module['special'] is not None:
                        stats = '{} {}'.format(stats, module['special'])
                    stored_modules_array.append('{} - {}'.format(module['name'], stats))
                stored_modules = '\n'.join(stored_modules_array)
                embed.add_field(name="Module Hangar",
                            value='{}'.format(stored_modules))
        await ctx.author.send(embed=embed)
