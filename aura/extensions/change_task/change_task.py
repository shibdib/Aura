import ast
import random

from discord.ext import commands

from aura.core import checks
from aura.lib import db
from aura.lib import game_assets
from aura.lib import game_functions
from aura.utils import make_embed


class ChangeTask:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session
        self.config = bot.config
        self.logger = bot.logger

    @commands.command(name='task', case_insensitive=True)
    @checks.spam_check()
    @checks.is_whitelist()
    @checks.has_account()
    async def change_task(self, ctx):
        """Change your current task."""
        if ctx.guild is not None:
            try:
                await ctx.message.delete()
            except Exception:
                pass
        sql = ''' SELECT * FROM eve_rpg_players WHERE `player_id` = (?) '''
        values = (ctx.message.author.id,)
        player = await db.select_var(sql, values)
        if player[0][6] == 20:
            await ctx.author.send('**ERROR** - You need to finish traveling first.')
            return await ctx.invoke(self.bot.get_command("me"), True)
        region_id = int(player[0][4])
        region_security = await game_functions.get_region_security(region_id)
        region_info = await game_functions.get_region_info(region_id)
        pirate_anomaly = False
        pirate_anomaly_text = ''
        if region_info[4] != 0:
            pirate_anomaly = True
            pirate_anomaly_text = "**7.** Run the combat anomalies in this region.\n"
        mining_anomaly = False
        mining_anomaly_text = ''
        if region_info[5] != 0:
            mining_anomaly = True
            mining_anomaly_text = "**11.** Mine the rich ore anomaly.\n"
        current_task = await game_functions.get_task(int(player[0][6]))
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        mission_destination = ''
        if player[0][22] is not None:
            mission_details = ast.literal_eval(player[0][22])
            region_name = await game_functions.get_region(mission_details['region'])
            mission_destination = '\nMission Location: {}'.format(region_name)
            if int(player[0][4]) == int(mission_details['region']):
                mission_task = '**9.** Warp to mission site.\n'
            else:
                mission_task = '**9.** Abandon Mission.\n'
        else:
            mission_task = '**9.** Request a Mission.\n'
        if player[0][16] is not None and player[0][16] != 0:
            fleet_task = '**5.** Fleet Options.\n'
        else:
            fleet_task = '**5.** Join Fleet.\n'
        if region_security != 'High':
            embed.add_field(name="Change Task",
                            value="**Current Task** - {}{}\n\n"
                                  "**Dock**\n"
                                  "**1.** Dock in current region.\n"
                                  "**PVP Tasks**\n"
                                  "**2.** Hunt for players.\n"
                                  "**3.** Camp a gate in your current region.\n"
                                  "{}"
                                  "**PVE Tasks**\n"
                                  "**6.** Kill belt rats.\n"
                                  "{}"
                                  "{}"
                                  "**Mining Tasks**\n"
                                  "**10.** Mine an asteroid belt.\n"
                                  "{}".format(current_task, mission_destination, fleet_task,
                                              pirate_anomaly_text, mission_task, mining_anomaly_text))
            accepted = [1, 2, 3, 5, 6, 8, 9, 10]
            if pirate_anomaly is True:
                accepted.append(7)
            if mining_anomaly is True:
                accepted.append(11)
        else:
            embed.add_field(name="Change Task",
                            value="**Current Task** - {}{}\n\n"
                                  "**Dock**\n"
                                  "**1.** Dock in current region.\n"
                                  "**PVP Tasks**\n"
                                  "**4.** Try to gank someone.\n"
                                  "{}"
                                  "**PVE Tasks**\n"
                                  "**6.** Kill belt rats.\n"
                                  "**8.** Do some exploration and run sites in the system.\n"
                                  "{}"
                                  "**Mining Tasks**\n"
                                  "**10.** Mine an asteroid belt.\n".format(current_task, mission_destination, fleet_task,
                                                                            mission_task))
            accepted = [1, 4, 6, 8, 9, 10]
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120.0)
        content = msg.content
        if content == '5':
            return await ctx.invoke(self.bot.get_command("fleet"))
        elif content == '2' and int(content) in accepted:
            await self.hunting_options(ctx, player[0])
        elif content == '9':
            await self.process_mission(ctx, player[0])
        elif int(content) in accepted:
            if content == '1' and player[0][25] is not None:
                return await ctx.author.send(
                    '**ERROR** - Your hostile actions have forced us to deny docking access for'
                    ' approximately {} more seconds.'.format(player[0][25] * 12))
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
            await ctx.author.send('**Task Updated** - You are now {}.'.format(new_task))
        elif '!!' not in content:
            await ctx.author.send('**ERROR** - Not a valid choice.')
        if content.find('!!') == -1:
            return await ctx.invoke(self.bot.get_command("me"), True)
        else:
            return

    async def process_mission(self, ctx, player):
        restrictions = game_assets.mission_restrictions
        if player[22] is not None:
            mission_details = ast.literal_eval(player[22])
            if int(player[4]) == int(mission_details['region']):
                ship_type = ast.literal_eval(player[14])['ship_type']
                ship = await game_functions.get_ship(int(ship_type))
                level = mission_details['level']
                if ship['class'] not in restrictions[level]:
                    await ctx.author.send('**That Class Of Ship Is Not Authorized In This Area**')
                    return await ctx.invoke(self.bot.get_command("me"), True)
                sql = ''' UPDATE eve_rpg_players
                        SET task = (?)
                        WHERE
                            player_id = (?); '''
                values = (9, ctx.author.id,)
                await db.execute_sql(sql, values)
                await ctx.author.send('**Entering Mission Site**')
                return await ctx.invoke(self.bot.get_command("me"), True)
            else:
                embed = make_embed(icon=ctx.bot.user.avatar)
                embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                                 text="Aura - EVE Text RPG")
                embed.add_field(name="Abandon Mission",
                                value="Are you sure you want to abandon this mission?\n\n"
                                      "It will cost you {} ISK\n\n"
                                      "**1.** Yes\n"
                                      "**2.** No".format('{0:,.2f}'.format(float(mission_details['failure']))))
                await ctx.author.send(embed=embed)

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.author.dm_channel

                msg = await self.bot.wait_for('message', check=check, timeout=120)
                content = msg.content
                if content == '2':
                    await ctx.author.send('**Mission Not Abandoned**')
                    return await ctx.invoke(self.bot.get_command("me"), True)
                elif content != '1':
                    await ctx.author.send('**Invalid Choice**')
                    if content.find('!!') == -1:
                        return await ctx.invoke(self.bot.get_command("me"), True)
                    else:
                        return
                sql = ''' UPDATE eve_rpg_players
                        SET mission_details = (?),
                            isk = (?)
                        WHERE
                            player_id = (?); '''
                values = (None, player[5] - int(float(mission_details['failure'])), ctx.author.id,)
                await db.execute_sql(sql, values)
                await ctx.author.send('**Mission Abandoned**')
                return await ctx.invoke(self.bot.get_command("me"), True)
        else:
            embed = make_embed(icon=ctx.bot.user.avatar)
            embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                             text="Aura - EVE Text RPG")
            embed.add_field(name="Request Mission",
                            value="What level mission are you looking for?\n\n"
                                  "*Higher level gets you better rewards, but the risk of death increases as well*\n\n"
                                  "**Respond with a number 1 - 5**")
            await ctx.author.send(embed=embed)

            def check(m):
                return m.author == ctx.author and m.channel == ctx.author.dm_channel

            msg = await self.bot.wait_for('message', check=check, timeout=120)
            content = msg.content
            mission = await game_functions.get_mission(content)
            if mission is None:
                await ctx.author.send('**No mission found for the requested level**')
                return await ctx.invoke(self.bot.get_command("me"), True)
            if int(content) < 3:
                reward = random.randint(35000 * int(content), 95000 * int(content))
                failure = random.randint(int(float(reward * 0.20)), int(float(reward * 0.60)))
            elif int(content) < 5:
                reward = random.randint(125000 * int(content), 550000 * int(content))
                failure = random.randint(int(float(reward * 0.20)), int(float(reward * 0.60)))
            else:
                reward = random.randint(525000 * int(content), 1000000 * int(content))
                failure = random.randint(int(float(reward * 0.20)), int(float(reward * 0.60)))
            region_id = random.randint(5, 20)
            region_name = await game_functions.get_region(region_id)
            accepted_classes = []
            for ship_class in restrictions[int(content)]:
                ship_class_name = game_assets.ship_classes[ship_class]
                accepted_classes.append(ship_class_name)
            ship_class_text = ', '.join(accepted_classes)
            embed = make_embed(icon=ctx.bot.user.avatar)
            embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                             text="Aura - EVE Text RPG")
            embed.add_field(name="Offered Mission",
                            value="__**{}**__\n\n"
                                  "{}\n\n"
                                  "**Mission Region:** {}\n"
                                  "**Accepted Ship Classes:** {}\n"
                                  "**Reward:** {} ISK\n"
                                  "**Failure Penalty:** {} ISK\n\n"
                                  "**1.** Accept\n"
                                  "**2.** Deny\n"
                                  "**3.** Request another mission\n".format(mission['name'], mission['initial'],
                                                                            region_name,
                                                                            ship_class_text,
                                                                            '{0:,.2f}'.format(float(reward)),
                                                                            '{0:,.2f}'.format(float(failure))))
            await ctx.author.send(embed=embed)

            def check(m):
                return m.author == ctx.author and m.channel == ctx.author.dm_channel

            msg = await self.bot.wait_for('message', check=check, timeout=120)
            content = msg.content
            if content == '3':
                return await self.process_mission(ctx, player)
            elif content == '2':
                await ctx.author.send('**Canceled**')
                return await ctx.invoke(self.bot.get_command("me"), True)
            elif content != '1':
                await ctx.author.send('**Invalid Choice**')
                if content.find('!!') == -1:
                    return await ctx.invoke(self.bot.get_command("me"), True)
                else:
                    return
            details = mission
            mission['region'] = region_id
            mission['reward'] = reward
            mission['failure'] = failure
            sql = ''' UPDATE eve_rpg_players
                    SET mission_details = (?)
                    WHERE
                        player_id = (?); '''
            values = (str(details), ctx.author.id,)
            await db.execute_sql(sql, values)
            embed = make_embed(icon=ctx.bot.user.avatar)
            embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                             text="Aura - EVE Text RPG")
            embed.add_field(name="Mission Assigned",
                            value="Start heading towards {}, once in system visit the "
                                  "tasks menu to enter the site".format(region_name))
            await ctx.author.send(embed=embed)
            return await ctx.invoke(self.bot.get_command("me"), True)

    async def hunting_options(self, ctx, player):
        region_id = int(player[4])
        region_info = await game_functions.get_region_info(region_id)
        accepted = [1, 2, 3]
        pirate_anomaly_text = ""
        if region_info[4] != 0:
            accepted.append(4)
            pirate_anomaly_text = "**4.** In the pirate anomaly.\n"
        mining_anomaly_text = ""
        if region_info[5] != 0:
            accepted.append(5)
            mining_anomaly_text = "**5.** In the ore anomaly.\n"
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Choose Target",
                        value="Where do you want to look for targets?\n\n"
                              "**1.** In the belts.\n"
                              "**2.** On the gates.\n"
                              "**3.** At safe spots.\n"
                              "{}{}".format(pirate_anomaly_text, mining_anomaly_text))
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120)
        content = int(msg.content)
        if content in accepted:
            sql = ''' UPDATE eve_rpg_players
                    SET task = (?)
                    WHERE
                        player_id = (?); '''
            values = (int(content) + 30, ctx.author.id,)
            await db.execute_sql(sql, values)
            player = await game_functions.refresh_player(player)
            new_task = await game_functions.get_task(int(player[6]))
            await ctx.author.send('**Task Updated** - You are now *{}*.'.format(new_task))
            return await ctx.invoke(self.bot.get_command("me"), True)
        else:
            return await ctx.invoke(self.bot.get_command("me"), True)
