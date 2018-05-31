import ast

from discord.ext import commands

from aura.core import checks
from aura.lib import db
from aura.lib import game_functions
from aura.utils import make_embed


class Assets:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session
        self.config = bot.config
        self.logger = bot.logger

    @commands.command(name='assets', case_insensitive=True)
    @checks.spam_check()
    @checks.is_whitelist()
    @checks.has_account()
    async def assets(self, ctx):
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
            ship_hangar = ast.literal_eval(player[0][15])
            if ship_hangar is not None:
                stored_ships_array = []
                for key, ships in ship_hangar.items():
                    for ship in ships:
                        region_name = await game_functions.get_region(key)
                        ship_name = await game_functions.get_ship_name(int(ship))
                        stored_ships_array.append('{} - {}'.format(ship_name, region_name))
                stored_ships = '\n'.join(stored_ships_array)
                embed.add_field(name="Ships",
                                value='{}'.format(stored_ships))
                return await ctx.author.send(embed=embed)
            module_hangar = ast.literal_eval(player[0][13])
            if module_hangar is not None:
                stored_modules_array = []
                for key, items in module_hangar.items():
                    for item in items:
                        region_name = await game_functions.get_region(key)
                        module_name = await game_functions.get_module_name(int(item))
                        stored_modules_array.append('{} - {}'.format(module_name, region_name))
                stored_modules = '\n'.join(stored_modules_array)
                embed.add_field(name="Modules",
                                value='{}'.format(stored_modules))
                return await ctx.author.send(embed=embed)
            await ctx.author.send(embed=embed)
