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
            try:
                await ctx.message.delete()
            except Exception:
                pass
        sql = ''' SELECT * FROM eve_rpg_players WHERE `player_id` = (?) '''
        values = (ctx.message.author.id,)
        player = await db.select_var(sql, values)
        if player[0][15] is None and player[0][13] is None:
            embed = make_embed(icon=ctx.bot.user.avatar)
            embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                             text="Aura - EVE Text RPG")
            embed.add_field(name="Asset List",
                            value='No Assets Found')
            await ctx.author.send(embed=embed)
        else:
            embed = make_embed(icon=ctx.bot.user.avatar)
            embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                             text="Aura - EVE Text RPG")
            if player[0][15] is not None:
                ship_hangar = ast.literal_eval(player[0][15])
                stored_ships_array = []
                count = 0
                for key, ships in ship_hangar.items():
                    for ship in ships:
                        region_name = await game_functions.get_region(key)
                        ship_name = await game_functions.get_ship_name(int(ship['ship_type']))
                        stored_ships_array.append('{} - {}'.format(ship_name, region_name))
                        if count >= 10:
                            count = 0
                            stored_ships = '\n'.join(stored_ships_array)
                            embed.add_field(name="Ships",
                                            value='{}'.format(stored_ships))
                            stored_ships_array = []
                            count += 1
                if len(stored_ships_array) > 0:
                    stored_ships = '\n'.join(stored_ships_array)
                    embed.add_field(name="Ships",
                                    value='{}'.format(stored_ships))
            if player[0][13] is not None:
                module_hangar = ast.literal_eval(player[0][13])
                stored_modules_array = []
                count = 0
                for key, items in module_hangar.items():
                    for item in items:
                        region_name = await game_functions.get_region(key)
                        module_name = await game_functions.get_module_name(int(item))
                        stored_modules_array.append('{} - {}'.format(module_name, region_name))
                        count += 1
                        if count >= 10:
                            count = 0
                            stored_modules = '\n'.join(stored_modules_array)
                            embed.add_field(name="Modules",
                                            value='{}'.format(stored_modules))
                            stored_modules_array = []
                            count += 1
                if len(stored_modules_array) > 0:
                    stored_modules = '\n'.join(stored_modules_array)
                    embed.add_field(name="Modules",
                                    value='{}'.format(stored_modules))
            if player[0][13] is None and player[0][15] is None:
                embed.add_field(name="Asset List",
                                value='No Assets Found')
            await ctx.author.send(embed=embed)
        return await ctx.invoke(self.bot.get_command("me"), True)
