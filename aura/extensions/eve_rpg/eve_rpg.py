from discord.ext import commands
from aura.lib import db
from aura.lib import game_functions
from aura.core import checks
from aura.utils import make_embed
import asyncio
import random


class EveRpg:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session
        self.config = bot.config
        self.logger = bot.logger
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.tick_loop())

    @commands.command(name='rpgTop', aliases=["rpgtop"])
    @checks.spam_check()
    @checks.is_whitelist()
    async def _rpg_top(self, ctx):
        """Get the top RPG players"""
        sql = ''' SELECT * FROM eve_rpg_players WHERE `player_id` = (?) '''
        values = (ctx.message.author.id,)
        result = await db.select_var(sql, values)
        sql = ''' SELECT * FROM eve_rpg_players ORDER BY `level` DESC LIMIT 10 '''
        top_levels = await db.select(sql)
        top_levels_array = []
        for levels in top_levels:
            top_levels_user = self.bot.get_user(int(levels[2]))
            top_levels_array.append('{} - Level {}'.format(top_levels_user.display_name, levels[9]))
        levels_list = '\n'.join(top_levels_array)
        sql = ''' SELECT * FROM eve_rpg_players ORDER BY `kills` DESC LIMIT 10 '''
        top_killers = await db.select(sql)
        top_killers_array = []
        for killers in top_killers:
            top_killer_user = self.bot.get_user(int(killers[2]))
            top_killers_array.append('{} - {} Kills'.format(top_killer_user.display_name, killers[11]))
        killers_list = '\n'.join(top_killers_array)
        if result is None:
            return await ctx.author.send('**Error** - No player found. You must be part of the game to view this')
        else:
            embed = make_embed(guild=ctx.guild)
            embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                             text="Provided Via Firetail Bot")
            embed.add_field(name="Level Leaderboard",
                            value=levels_list, inline=False)
            embed.add_field(name="Kills Leaderboard",
                            value=killers_list, inline=False)
            await ctx.channel.send(embed=embed)

    async def tick_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                await self.process_travel()
                await self.process_belt_ratting()
                await self.process_anomaly_ratting()
                await self.process_roams()
                await asyncio.sleep(12)
            except Exception:
                self.logger.exception('ERROR:')
                await asyncio.sleep(5)

    async def process_travel(self):
        sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 20 '''
        travelers = await db.select(sql)
        if travelers is None or len(travelers) is 0:
            return
        for traveler in travelers:
            region_id = int(traveler[4])
            region_security = await game_functions.get_region_security(region_id)
            destination_id = int(traveler[17])
            destination_security = await game_functions.get_region_security(destination_id)
            sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 3 AND `region` = (?) '''
            values = (region_id,)
            outbound_campers = await db.select_var(sql, values)
            sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 3 AND `region` = (?) '''
            values = (destination_id,)
            inbound_campers = await db.select_var(sql, values)
            if len(outbound_campers) is not 0 and region_security != 'High':
                defender_ship_id = traveler[14]
                defender_attack, defender_defense, defender_maneuver, defender_tracking = \
                    await game_functions.get_combat_attributes(defender_ship_id)
                for camper in outbound_campers:
                    conflict = await self.weighted_choice([(True, 25 - defender_maneuver), (False, 65), (None, 45)])
                    if conflict is True:
                        await self.solo_combat(camper, traveler)
                        return
            if len(inbound_campers) is not 0 and destination_security != 'High':
                defender_ship_id = traveler[14]
                defender_attack, defender_defense, defender_maneuver, defender_tracking = \
                    await game_functions.get_combat_attributes(defender_ship_id)
                for camper in inbound_campers:
                    conflict = await self.weighted_choice([(True, 50 - defender_maneuver), (False, 65), (None, 45)])
                    if conflict is True:
                        await self.solo_combat(camper, traveler)
                        continue
            destination_name = await game_functions.get_region(destination_id)
            sql = ''' UPDATE eve_rpg_players
                    SET region = (?),
                        task = 21
                    WHERE
                        player_id = (?); '''
            values = (int(destination_id), traveler[2],)
            await db.execute_sql(sql, values)
            player = self.bot.get_user(traveler[2])
            sql = ''' SELECT * FROM eve_rpg_players WHERE `region` = (?) '''
            values = (destination_id,)
            local_players = await db.select_var(sql, values)
            return await player.send('You have arrived in {}\n\nLocal Count - {}'.format(destination_name,
                                                                                         len(local_players)))

    async def process_belt_ratting(self):
        sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 6 '''
        ratters = await db.select(sql)
        if ratters is None or len(ratters) is 0:
            return
        for ratter in ratters:
            region_id = int(ratter[4])
            region_name = await game_functions.get_region(int(region_id))
            user = self.bot.get_user(ratter[2])
            region_security = await game_functions.get_region_security(region_id)
            sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 6 AND `region` = (?) '''
            values = (region_id,)
            system_ratters = await db.select_var(sql, values)
            isk = await self.weighted_choice([(1000, 100), (1500, 30), (3500, 10)])
            if region_security == 'Low':
                isk = await self.weighted_choice([(2500, 100), (3500, 30), (5500, 10)])
            elif region_security == 'Null':
                isk = await self.weighted_choice([(7500, 100), (9500, 30), (13500, 10)])
            #  PVE Rolls
            ship_id = ratter[14]
            ship = await game_functions.get_ship_name(ship_id)
            ship_attack, ship_defense, ship_maneuver, ship_tracking = \
                await game_functions.get_combat_attributes(ship_id)
            death = await self.weighted_choice(
                [(True, 2), (False, 95 + ((ship_defense * 2.5) + (ship_maneuver * 1.2)))])
            flee = await self.weighted_choice(
                [(True, 13 + (ship_defense + (ship_maneuver * 2))), (False, 80 - (ship_maneuver * 2.5))])
            find_rats = await self.weighted_choice([(True, 150 / len(system_ratters)), (False, 40)])
            if find_rats is False:
                continue
            if death is True and flee is False:
                embed = make_embed(icon=self.bot.user.avatar)
                embed.set_footer(icon_url=self.bot.user.avatar_url,
                                 text="Aura - EVE Text RPG")
                ship_image = await game_functions.get_ship_image(ship_id)
                embed.set_thumbnail(url="{}".format(ship_image))
                embed.add_field(name="Killmail",
                                value="**Region** - {}\n\n"
                                      "**Loser**\n"
                                      "**{}** flying a {} was killed by belt rats.".format(region_name,
                                                                                           user.display_name,
                                                                                           ship))
                await self.destroy_ship(ratter)
                await self.add_loss(ratter)
                player = self.bot.get_user(ratter[2])
                await player.send(embed=embed)
                return await self.send_global(embed, True)
            elif flee is True:
                ratter_user = self.bot.get_user(ratter[2])
                await ratter_user.send('**NOTICE** - You nearly died to belt rats but managed to warp off.')
            else:
                xp_gained = await self.weighted_choice([(3, 45), (5, 15), (7, 5)])
                await self.add_xp(ratter, xp_gained)
                await self.add_isk(ratter, isk)

    async def process_anomaly_ratting(self):
        sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 7 '''
        ratters = await db.select(sql)
        if ratters is None or len(ratters) is 0:
            return
        for ratter in ratters:
            region_id = int(ratter[4])
            region_name = await game_functions.get_region(int(region_id))
            user = self.bot.get_user(ratter[2])
            region_security = await game_functions.get_region_security(region_id)
            sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 7 AND `region` = (?) '''
            values = (region_id,)
            system_ratters = await db.select_var(sql, values)
            isk = await self.weighted_choice([(5000, 100), (7500, 30), (9500, 10)])
            if region_security == 'Low':
                isk = await self.weighted_choice([(8500, 100), (11500, 30), (14500, 10)])
            elif region_security == 'Null':
                isk = await self.weighted_choice([(10500, 100), (14500, 30), (25500, 10)])
            #  PVE Rolls
            ship_id = ratter[14]
            ship = await game_functions.get_ship_name(ship_id)
            ship_attack, ship_defense, ship_maneuver, ship_tracking = \
                await game_functions.get_combat_attributes(ship_id)
            death = await self.weighted_choice(
                [(True, 12), (False, 90 + ((ship_defense * 2.5) + (ship_maneuver * 1.2)))])
            flee = await self.weighted_choice(
                [(True, 13 + (ship_defense + (ship_maneuver * 2))), (False, 80 - (ship_maneuver * 2.5))])
            find_rats = await self.weighted_choice([(True, 150 / len(system_ratters)), (False, 40)])
            if find_rats is False:
                continue
            if death is True and flee is False:
                embed = make_embed(icon=self.bot.user.avatar)
                embed.set_footer(icon_url=self.bot.user.avatar_url,
                                 text="Aura - EVE Text RPG")
                ship_image = await game_functions.get_ship_image(ship_id)
                embed.set_thumbnail(url="{}".format(ship_image))
                embed.add_field(name="Killmail",
                                value="**Region** - {}\n\n"
                                      "**Loser**\n"
                                      "**{}** flying a {} was killed while running an anomaly.".format(region_name,
                                                                                                       user.display_name,
                                                                                                       ship))
                await self.destroy_ship(ratter)
                await self.add_loss(ratter)
                player = self.bot.get_user(ratter[2])
                await player.send(embed=embed)
                return await self.send_global(embed, True)
            elif flee is True:
                ratter_user = self.bot.get_user(ratter[2])
                await ratter_user.send('**NOTICE** - You nearly died to anomaly rats but managed to warp off.')
            else:
                xp_gained = await self.weighted_choice([(3, 45), (5, 15), (7, 5)])
                await self.add_xp(ratter, xp_gained)
                await self.add_isk(ratter, isk)

    async def process_roams(self):
        sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 2 '''
        roamers = await db.select(sql)
        if roamers is None or len(roamers) is 0:
            return
        for roamer in roamers:
            region_id = int(roamer[4])
            region_security = await game_functions.get_region_security(region_id)
            sql = ''' SELECT * FROM eve_rpg_players WHERE `task` != 1 AND `region` = (?) AND `player_id` != (?) '''
            values = (region_id, roamer[2])
            potential_targets = await db.select_var(sql, values)
            if len(potential_targets) is 0 or region_security == 'High':
                continue
            else:
                for target in potential_targets:
                    target_aggression = 5
                    if 1 < int(target[6]) < 5:
                        target_aggression = 45
                    conflict = await self.weighted_choice([(True, target_aggression), (False, 65), (None, 45)])
                    if conflict is None:
                        break
                    elif conflict is True:
                        await self.solo_combat(roamer, target)
                        break

    async def solo_combat(self, attacker, defender):
        attacker_ship_id = attacker[14]
        defender_ship_id = defender[14]
        attacker_attack, attacker_defense, attacker_maneuver, attacker_tracking = \
            await game_functions.get_combat_attributes(attacker_ship_id)
        defender_attack, defender_defense, defender_maneuver, defender_tracking = \
            await game_functions.get_combat_attributes(defender_ship_id)
        tracking_one = 1
        if attacker_tracking < defender_maneuver:
            tracking_one = 0.8
        tracking_two = 1
        if defender_tracking < attacker_maneuver:
            tracking_two = 0.8
        pve_disadvantage = 0
        if 5 < int(defender[6]) < 11:
            pve_disadvantage = 2
        player_one_weight = (((attacker[8] + 1) * 0.5) + (attacker_attack - (defender_defense / 2))) * tracking_one
        player_two_weight = ((((defender[8] + 1) * 0.5) + (defender_attack -
                                                           (attacker_defense / 2))) * tracking_two) - pve_disadvantage
        winner = await self.weighted_choice([(attacker, player_one_weight), (defender, player_two_weight)])
        loser = attacker
        winner_catch = defender_attack / 2 + defender_tracking
        loser_escape = attacker_defense / 2 + attacker_maneuver
        if winner is attacker:
            loser = defender
            winner_catch = attacker_attack / 2 + attacker_tracking
            loser_escape = defender_defense / 2 + defender_maneuver
        escape = False
        if loser_escape > winner_catch:
            escape = await self.weighted_choice([(True, loser_escape), (False, winner_catch)])
        winner_name = self.bot.get_user(int(winner[2])).display_name
        region_id = int(winner[4])
        region_name = await game_functions.get_region(int(region_id))
        loser_name = self.bot.get_user(int(loser[2])).display_name
        winner_ship = await game_functions.get_ship_name(int(winner[14]))
        winner_task = await game_functions.get_task(int(winner[6]))
        loser_ship = await game_functions.get_ship_name(int(loser[14]))
        loser_task = await game_functions.get_task(int(loser[6]))
        if escape is False:
            xp_gained = await self.weighted_choice([(5, 45), (15, 15), (27, 5)])
            embed = make_embed(icon=self.bot.user.avatar)
            embed.set_footer(icon_url=self.bot.user.avatar_url,
                             text="Aura - EVE Text RPG")
            ship_image = await game_functions.get_ship_image(loser[14])
            embed.set_thumbnail(url="{}".format(ship_image))
            embed.add_field(name="Killmail",
                            value="**Region** - {}\n\n"
                                  "**Loser**\n"
                                  "**{}** flying a {} was killed while they were {}.\n\n"
                                  "**Killer**\n"
                                  "**{}** flying a {} while {}.\n\n".format(region_name, loser_name, loser_ship,
                                                                            loser_task,
                                                                            winner_name, winner_ship, winner_task))
            winner_user = self.bot.get_user(winner[2])
            loser_user = self.bot.get_user(loser[2])
            await winner_user.send(embed=embed)
            await loser_user.send(embed=embed)
            await self.send_global(embed, True)
            await self.destroy_ship(loser)
            await self.add_loss(loser)
            await self.add_kill(winner)
            await self.add_xp(winner, xp_gained)
        else:
            winner_user = self.bot.get_user(winner[2])
            loser_user = self.bot.get_user(loser[2])
            await winner_user.send('**PVP** - Combat between you and a {} flown by {}, they nearly died to your {} but '
                                   'managed to warp off and dock.'.format(loser_ship, loser_name, winner_ship))
            await loser_user.send('**PVP** - Combat between you and a {} flown by {}, you nearly lost your {} but '
                                  'managed to break tackle and dock.'.format(winner_ship, winner_name, loser_ship))
            sql = ''' UPDATE eve_rpg_players
                    SET task = 1
                    WHERE
                        player_id = (?); '''
            values = (loser[2],)
            await db.execute_sql(sql, values)

    async def weighted_choice(self, items):
        """items is a list of tuples in the form (item, weight)"""
        weight_total = sum((item[1] for item in items))
        n = random.uniform(0, weight_total)
        for item, weight in items:
            if n < weight:
                return item
            n = n - weight
        return item

    async def send_global(self, message, embed=False):
        sql = "SELECT * FROM eve_rpg_channels"
        game_channels = await db.select(sql)
        for channels in game_channels:
            channel = self.bot.get_channel(int(channels[2]))
            if channel is None:
                self.logger.exception('eve_rpg - Bad Channel Attempted removing....')
                await self.remove_bad_channel(channels[2])
            if embed is False:
                await channel.send(message)
            else:
                await channel.send(embed=message)

    async def remove_bad_user(self, player_id):
        sql = ''' DELETE FROM eve_rpg_players WHERE `player_id` = (?) '''
        values = (player_id,)
        await db.execute_sql(sql, values)
        return self.logger.info('eve_rpg - Bad player removed successfully')

    async def remove_bad_channel(self, channel_id):
        sql = ''' DELETE FROM eve_rpg_channels WHERE `channel_id` = (?) '''
        values = (channel_id,)
        await db.execute_sql(sql, values)
        return self.logger.info('eve_rpg - Bad Channel removed successfully')

    async def add_xp(self, player, xp_gained):
        if player[10] + xp_gained < 100:
            sql = ''' UPDATE eve_rpg_players
                    SET xp = (?)
                    WHERE
                        player_id = (?); '''
            values = (player[10] + xp_gained, player[2],)
        else:
            sql = ''' UPDATE eve_rpg_players
                    SET level = (?),
                        xp = (?)
                    WHERE
                        player_id = (?); '''
            values = (player[9] + 1, 0, player[2],)
        await db.execute_sql(sql, values)

    async def add_isk(self, player, isk):
        sql = ''' UPDATE eve_rpg_players
                SET isk = (?)
                WHERE
                    player_id = (?); '''
        values = (int(player[5]) + isk, player[2],)
        await db.execute_sql(sql, values)

    async def add_kill(self, player):
        sql = ''' UPDATE eve_rpg_players
                SET kills = (?)
                WHERE
                    player_id = (?); '''
        values = (int(player[10]) + 1, player[2],)
        await db.execute_sql(sql, values)

    async def add_loss(self, player):
        sql = ''' UPDATE eve_rpg_players
                SET losses = (?)
                WHERE
                    player_id = (?); '''
        values = (int(player[11]) + 1, player[2],)
        await db.execute_sql(sql, values)

    async def destroy_ship(self, player):
        ship_id = 1
        region_id = 1
        if player[3] == 1:
            ship_id = 1
            region_id = 1
        elif player[3] == 2:
            ship_id = 2
            region_id = 2
        elif player[3] == 3:
            ship_id = 3
            region_id = 3
        elif player[3] == 4:
            ship_id = 5
            region_id = 4
        elif player[3] == 99:
            ship_id = 5
            region_id = 1
        sql = ''' UPDATE eve_rpg_players
                SET ship = (?),
                    modules = NULL,
                    region = (?),
                    task = 21
                WHERE
                    player_id = (?); '''
        values = (ship_id, region_id, player[2],)
        await db.execute_sql(sql, values)
