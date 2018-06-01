import ast

from discord.ext import commands

from aura.core import checks
from aura.lib import db
from aura.lib import game_functions
from aura.utils import make_embed


class Hangar:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session
        self.config = bot.config
        self.logger = bot.logger

    @commands.command(name='hangar', case_insensitive=True)
    @checks.spam_check()
    @checks.is_whitelist()
    @checks.has_account()
    async def ship_hangar(self, ctx):
        """Visit your regional ship hangar."""
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
        current_ship = await game_functions.get_ship_name(int(player_ship_obj['ship_type']))
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
            current_hangar = ship_hangar[player[0][4]]
            stored_ships_array = []
            owned_ship_ids = []
            ship_number = 1
            for ship in ship_hangar[player[0][4]]:
                owned_ship_ids.append(ship_number)
                ship['selection'] = ship_number
                ship_name = await game_functions.get_ship_name(int(ship['ship_type']))
                stored_ships_array.append('{}. {}'.format(ship_number, ship_name))
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
                        insert_this = ship
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
                current_ship = ast.literal_eval(player[0][14])
                if content != '1':
                    return await ctx.author.send('**Switch Canceled**')
                for ship in ship_hangar[player[0][4]]:
                    if ship['id'] == ship_id:
                        remove = ship
                        break
                ship_hangar[player[0][4]].remove(remove)
                new_hangar = ship_hangar
                insert_this.pop('selection', None)
                if new_hangar is None:
                    new_hangar = {player[0][4]: [current_ship]}
                else:
                    new_hangar[player[0][4]].append(current_ship)
                if player[0][12] is not None:
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
                    values = (str(insert_this), str(new_hangar), str(module_hangar), ctx.author.id,)
                else:
                    values = (str(insert_this), str(new_hangar), player[0][13], ctx.author.id,)
                sql = ''' UPDATE eve_rpg_players
                        SET ship = (?),
                            ship_hangar = (?),
                            modules = NULL,
                            module_hangar = (?)
                        WHERE
                            player_id = (?); '''
                await db.execute_sql(sql, values)
                return await ctx.author.send('**A {} Is Now Your Active Ship**'.format(selected_ship['name']))
            else:
                return await ctx.author.send('**ERROR** - Not a valid choice.')
