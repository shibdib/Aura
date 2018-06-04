import ast

from discord.ext import commands

from aura.core import checks
from aura.lib import db
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
    async def _me(self, ctx, redirect=False):
        """Manage your character."""
        if ctx.guild is not None:
            try:
                await ctx.message.delete()
            except Exception:
                pass
        if ctx.invoked_subcommand is None:
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
            player_ship_obj = ast.literal_eval(player[0][14])
            module_cargo_option = ''
            if 'module_cargo_bay' in player_ship_obj and int(player[0][6]) == 1:
                module_cargo_option = '**8.** Empty Module Cargo Bay\n'
            component_cargo_option = ''
            if 'component_cargo_bay' in player_ship_obj and int(player[0][6]) == 1:
                component_cargo_option = '**9.** Empty Component Cargo Bay\n'
            current_ship_raw = await game_functions.get_ship_name(int(player_ship_obj['ship_type']))
            current_ship = current_ship_raw
            wallet_balance = '{0:,.2f}'.format(float(player[0][5]))
            embed = make_embed(icon=ctx.bot.user.avatar)
            embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                             text="Aura - EVE Text RPG")
            timeout = 60
            if int(player[0][6]) == 20:
                destination = await game_functions.get_region(int(player[0][17]))
                embed.add_field(name="Welcome {}".format(player_name),
                                value="**Current Region** - {}\n**Local Count** - {}\n**Current Ship** - {}\n"
                                      "**Current Task** - {}\n**Wallet Balance** - {}\n\n"
                                      "*Ship is currently traveling to {}.......*".format(
                                    region_name, len(local_players), current_ship, current_task, wallet_balance,
                                    destination))
                return await ctx.author.send(embed=embed)
            if redirect is False:
                embed.add_field(name="Welcome {}".format(player_name),
                                value="**Current Region** - {}\n**Local Count** - {}\n**Current Ship** - {}\n"
                                      "**Current Task** - {}\n**Wallet Balance** - {}\n\n"
                                      "*User interface initiated.... Select desired action below......*\n\n"
                                      "**1.** Change task.\n"
                                      "**2.** Travel to a new region.\n"
                                      "**3.** Modify current ship.\n"
                                      "**4.** Change into another ship.\n"
                                      "**5.** Visit the regional market.\n"
                                      "**6.** View your asset list.\n"
                                      "**7.** Insure your ship.\n"
                                      "{}"
                                      "{}"
                                      "**10.** Change your clone to here.\n"
                                      "**11.** View Local.\n".format(
                                    region_name, len(local_players), current_ship, current_task, wallet_balance,
                                    module_cargo_option, component_cargo_option))
            if redirect is True:
                timeout = None
                embed.add_field(name="Welcome {}".format(player_name),
                                value="**1.** Change task.\n"
                                      "**2.** Travel to a new region.\n"
                                      "**3.** Modify current ship.\n"
                                      "**4.** Change into another ship.\n"
                                      "**5.** Visit the regional market.\n"
                                      "**6.** View your asset list.\n"
                                      "**7.** Insure your ship.\n"
                                      "{}"
                                      "{}"
                                      "**10.** Change your clone to here.\n"
                                      "**11.** View Local.\n".format(module_cargo_option, component_cargo_option))
            await ctx.author.send(embed=embed)

            def check(m):
                return m.author == ctx.author and m.channel == ctx.author.dm_channel

            msg = await self.bot.wait_for('message', check=check, timeout=timeout)
            content = msg.content
            if content == '1':
                await ctx.invoke(self.bot.get_command("task"))
            elif content == '2':
                await ctx.invoke(self.bot.get_command("travel"))
            elif content == '3':
                await ctx.invoke(self.bot.get_command("fitting"))
            elif content == '4':
                await ctx.invoke(self.bot.get_command("hangar"))
            elif content == '5':
                await ctx.invoke(self.bot.get_command("market"))
            elif content == '6':
                await ctx.invoke(self.bot.get_command("assets"))
            elif content == '7':
                await self.insure_ship(ctx, player)
            elif content == '8' and 'module_cargo_bay' in player_ship_obj and int(player[0][6]) == 1:
                await self.empty_module_cargo(ctx)
            elif content == '9' and 'component_cargo_bay' in player_ship_obj and int(player[0][6]) == 1:
                await self.empty_component_cargo(ctx)
            elif content == '10':
                await self.change_clone(ctx, player)
            elif content == '11':
                await ctx.invoke(self.bot.get_command("local"))
            else:
                return await ctx.author.send('**ERROR** - Not a valid choice.')

    async def insure_ship(self, ctx, player):
        """Insure your current ship."""
        if player[0][6] is not 1:
            return await ctx.author.send('**ERROR** - You must be docked to do this.')
        ship = ast.literal_eval(player[0][14])
        if 'insured' in ship:
            return await ctx.author.send('**Your current ship is already insured**')
        current_ship = await game_functions.get_ship(ship['ship_type'])
        raw_cost = current_ship['isk'] * 0.2
        insurance_cost = '{0:,.2f}'.format(float(raw_cost))
        insurance_payout = current_ship['isk'] * 0.8
        embed = make_embed(icon=self.bot.user.avatar)
        embed.set_footer(icon_url=self.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Insure Ship",
                        value="Insurance is an upfront payment equivalent to 20% of the current ship price, in return "
                              "upon your untimely death you will receive 80% of the insured value of your ship back.\n\n"
                              "It will cost **{} ISK** to insure your {}\n\n"
                              "Is this acceptable?\n"
                              "**1.** Yes.\n"
                              "**2.** No.\n".format(insurance_cost, current_ship['name']))
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120.0)
        content = int(msg.content)
        if content != 1:
            await ctx.author.send('**Insurance Contract Canceled**')
            return await ctx.invoke(self.bot.get_command("me"), True)
        if int(float(player[0][5])) < int(float(raw_cost)):
            await ctx.author.send('**Not enough ISK**')
            return await ctx.invoke(self.bot.get_command("me"), True)
        sql = ''' UPDATE eve_rpg_players
                SET ship = (?),
                    isk = (?)
                WHERE
                    player_id = (?); '''
        ship['insured'] = True
        ship['insurance_payout'] = insurance_payout
        remaining_isk = int(float(player[0][5])) - int(float(raw_cost))
        values = (str(ship), remaining_isk, ctx.author.id,)
        await db.execute_sql(sql, values)
        await ctx.author.send('**Insurance purchased for a {}**'.format(current_ship['name']))
        return await ctx.invoke(self.bot.get_command("me"), True)

    async def empty_module_cargo(self, ctx):
        sql = ''' SELECT * FROM eve_rpg_players WHERE `player_id` = (?) '''
        values = (ctx.message.author.id,)
        player = await db.select_var(sql, values)
        player_ship_obj = ast.literal_eval(player[0][14])
        new_modules = []
        for module in player_ship_obj['module_cargo_bay']:
            new_modules.append(module)
        if player[0][13] is None:
            current_hangar = {player[0][4]: new_modules}
        elif player[0][4] not in ast.literal_eval(player[0][13]):
            current_hangar = ast.literal_eval(player[0][13])
            current_hangar[player[0][4]] = new_modules
        else:
            current_hangar = ast.literal_eval(player[0][13])
            for component in new_modules:
                current_hangar[player[0][4]].append(component)
        sql = ''' UPDATE eve_rpg_players
                SET ship = (?),
                    module_hangar = (?)
                WHERE
                    player_id = (?); '''
        values = (str(player_ship_obj), str(current_hangar), ctx.author.id,)
        await db.execute_sql(sql, values)
        return await ctx.author.send('**Module Cargo Bay Emptied Into Your Regional Hangar**')

    async def empty_component_cargo(self, ctx):
        sql = ''' SELECT * FROM eve_rpg_players WHERE `player_id` = (?) '''
        values = (ctx.message.author.id,)
        player = await db.select_var(sql, values)
        player_ship_obj = ast.literal_eval(player[0][14])
        new_components = []
        for module in player_ship_obj['component_cargo_bay']:
            new_components.append(module)
        if player[0][19] is None:
            current_hangar = {player[0][4]: new_components}
        elif player[0][4] not in ast.literal_eval(player[0][19]):
            current_hangar = ast.literal_eval(player[0][19])
            current_hangar[player[0][4]] = new_components
        else:
            current_hangar = ast.literal_eval(player[0][19])
            for component in new_components:
                current_hangar[player[0][4]].append(component)
        player_ship_obj.pop('component_cargo_bay', None)
        sql = ''' UPDATE eve_rpg_players
                SET ship = (?),
                    component_hangar = (?)
                WHERE
                    player_id = (?); '''
        values = (str(player_ship_obj), str(current_hangar), ctx.author.id,)
        await db.execute_sql(sql, values)
        await ctx.author.send('**Component Cargo Bay Emptied Into Your Regional Hangar**')
        return await ctx.invoke(self.bot.get_command("me"), True)

    async def change_clone(self, ctx, player):
        """Change your clone location."""
        if player[0][18] is player[0][4]:
            await ctx.author.send('**This region is already your clone location**')
            return await ctx.invoke(self.bot.get_command("me"), True)
        home_region_name = await game_functions.get_region(player[0][18])
        current_region_name = await game_functions.get_region(player[0][4])
        embed = make_embed(icon=self.bot.user.avatar)
        embed.set_footer(icon_url=self.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Change Clone Location",
                        value="Are you sure you want to change your clone location from **{}** to **{}**\n\n*Relocating"
                              " your clone costs 10,000 ISK*\n\n"
                              "**1.** Yes.\n"
                              "**2.** No.\n".format(home_region_name, current_region_name))
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120.0)
        content = int(msg.content)
        if content != 1:
            await ctx.author.send('**Clone Location Not Changed**')
            return await ctx.invoke(self.bot.get_command("me"), True)
        if int(float(player[0][5])) < int(float(10000)):
            await ctx.author.send('**Not enough ISK**')
            return await ctx.invoke(self.bot.get_command("me"), True)
        sql = ''' UPDATE eve_rpg_players
                SET home = (?),
                    isk = (?)
                WHERE
                    player_id = (?); '''
        remaining_isk = int(float(player[0][5])) - int(float(10000))
        values = (player[0][4], remaining_isk, ctx.author.id,)
        await db.execute_sql(sql, values)
        await ctx.author.send('**Clone Location Changed**')
        return await ctx.invoke(self.bot.get_command("me"), True)
