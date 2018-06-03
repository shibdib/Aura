import ast
import asyncio
import random

from aura.lib import db
from aura.lib import game_functions
from aura.utils import make_embed


class EveRpg:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session
        self.config = bot.config
        self.logger = bot.logger
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.tick_loop())
        self.user_check_counter = 0

    async def tick_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                await self.process_travel()
                await self.process_belt_ratting()
                await self.process_belt_mining()
                await self.process_anomaly_ratting()
                await self.process_roams()
                await self.process_ganks()
                await self.process_users()
                await asyncio.sleep(12)
            except Exception:
                self.logger.exception('ERROR:')
                await asyncio.sleep(5)

    async def process_users(self):
        if self.user_check_counter >= 100:
            sql = "SELECT * FROM eve_rpg_players"
            players = await db.select(sql)
            for player in players:
                user = self.bot.get_user(player[2])
                if user is None:
                    await self.remove_bad_user(player[2])
                    continue
        else:
            self.user_check_counter += 1

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
            traveler_ship = ast.literal_eval(traveler[14])
            defender_ship_id = traveler_ship['ship_type']
            defender_attack, defender_defense, defender_maneuver, defender_tracking = \
                await game_functions.get_combat_attributes(traveler, defender_ship_id)
            if len(outbound_campers) is not 0 and region_security != 'High':
                for camper in outbound_campers:
                    conflict = await self.weighted_choice([(True, 35 - defender_maneuver), (False, 65), (None, 45)])
                    if conflict is True:
                        await self.solo_combat(camper, traveler)
                        return
            if len(inbound_campers) is not 0 and destination_security != 'High':
                for camper in inbound_campers:
                    conflict = await self.weighted_choice([(True, 60 - defender_maneuver), (False, 65), (None, 45)])
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
            ratter_ship = ast.literal_eval(ratter[14])
            ship_id = ratter_ship['ship_type']
            ship = await game_functions.get_ship(ship_id)
            isk = random.randint(1000, 3500)
            survival = 400
            npc = 125
            if region_security == 'Low':
                isk = random.randint(5500, 9500)
                survival = 275
                npc = 225
            elif region_security == 'Null':
                isk = random.randint(8500, 19500)
                survival = 225
                npc = 350
            if ship['class'] == 1:
                survival = 175
                if region_security == 'Low':
                    survival = 50
                elif region_security == 'Null':
                    survival = -10
            #  PVE Rolls
            ship_name = await game_functions.get_ship_name(ship_id)
            ship_attack, ship_defense, ship_maneuver, ship_tracking = \
                await game_functions.get_combat_attributes(ratter, ship_id)
            death = await self.weighted_choice(
                [(True, 2), (False, survival + ((ship_defense * 11) + (ship_maneuver * 6) +
                                                (ship_attack * 8)))])
            flee = await self.weighted_choice(
                [(True, 13 + (ship_defense + (ship_maneuver * 2))), (False, 80 - (ship_maneuver * 2.5))])
            find_rats = await self.weighted_choice([(True, npc / len(system_ratters)), (False, 40)])
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
                                                                                           ship_name))
                await self.add_loss(ratter)
                player = self.bot.get_user(ratter[2])
                await player.send(embed=embed)
                await self.send_global(embed, True)
                return await self.destroy_ship(ratter)
            elif flee is True:
                ratter_user = self.bot.get_user(ratter[2])
                # await ratter_user.send('**NOTICE** - You nearly died to belt rats but managed to warp off.')
            else:
                xp_gained = await self.weighted_choice([(1, 35), (3, 15), (0, 15)])
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
            ratter_ship = ast.literal_eval(ratter[14])
            ship_id = ratter_ship['ship_type']
            ship = await game_functions.get_ship(ship_id)
            isk = random.randint(1000, 3500)
            survival = 300
            npc = 125
            if region_security == 'Low':
                isk = random.randint(7500, 25500)
                survival = 200
                npc = 225
            elif region_security == 'Null':
                isk = random.randint(17500, 45500)
                survival = 155
                npc = 350
            if ship['class'] == 1:
                survival = 175
                if region_security == 'Low':
                    survival = 25
                elif region_security == 'Null':
                    survival = -25
            #  PVE Rolls
            ship_name = await game_functions.get_ship_name(ship_id)
            ship_attack, ship_defense, ship_maneuver, ship_tracking = \
                await game_functions.get_combat_attributes(ratter, ship_id)
            death = await self.weighted_choice(
                [(True, 12), (False, survival + ((ship_defense * 11) + (ship_maneuver * 6) +
                                                 (ship_attack * 8)))])
            flee = await self.weighted_choice(
                [(True, 13 + (ship_defense + (ship_maneuver * 2))), (False, 80 - (ship_maneuver * 2.5))])
            find_rats = await self.weighted_choice([(True, npc / len(system_ratters)), (False, 40)])
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
                                                                                                       ship_name))
                await self.add_loss(ratter)
                await user.send(embed=embed)
                await self.send_global(embed, True)
                return await self.destroy_ship(ratter)
            elif flee is True:
                ratter_user = self.bot.get_user(ratter[2])
                # await ratter_user.send('**NOTICE** - You nearly died to anomaly rats but managed to warp off.')
            else:
                xp_gained = await self.weighted_choice([(2, 35), (3, 15), (0, 15)])
                await self.add_xp(ratter, xp_gained)
                await self.add_isk(ratter, isk)

    async def process_belt_mining(self):
        sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 9 '''
        miners = await db.select(sql)
        if miners is None or len(miners) is 0:
            return
        for miner in miners:
            region_id = int(miner[4])
            region_security = await game_functions.get_region_security(region_id)
            region_name = await game_functions.get_region(int(region_id))
            user = self.bot.get_user(miner[2])
            sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 9 AND `region` = (?) '''
            values = (region_id,)
            belt_miners = await db.select_var(sql, values)
            isk = random.randint(100, 550)
            miner_ship = ast.literal_eval(miner[14])
            ship_id = miner_ship['ship_type']
            ship = await game_functions.get_ship(ship_id)
            possible_npc = False
            survival = 500
            ore = 100
            if region_security == 'Low':
                survival = 350
                ore = 150
                possible_npc = 2
                isk = random.randint(800, 1700)
            elif region_security == 'Null':
                survival = 275
                ore = 300
                possible_npc = 4
                isk = random.randint(950, 3250)
            if ship['class'] == 1:
                survival = 175
                if region_security == 'Low':
                    survival = 25
                elif region_security == 'Null':
                    survival = 0
            find_ore = await self.weighted_choice([(True, ore / len(belt_miners)), (False, 40)])
            if find_ore is False:
                continue
            else:
                #  Ship multi
                miner_ship = ast.literal_eval(miner[14])
                ship_id = miner_ship['ship_type']
                ship = await game_functions.get_ship(ship_id)
                multiplier = 1
                defense_multi = 1
                if ship['class'] == 6:
                    multiplier = 1.75
                    defense_multi = 1.5
                if ship['id'] == 80:
                    multiplier = 2.4
                    defense_multi = 4
                if ship['id'] == 81:
                    multiplier = 3
                    defense_multi = 2
                if ship['id'] == 90:
                    multiplier = 2.9
                    defense_multi = 6
                if ship['id'] == 91:
                    multiplier = 4
                    defense_multi = 2.5
                if miner[12] is not None:
                    modules = ast.literal_eval(miner[12])
                    for module in modules:
                        if module == 17:
                            isk = (isk * .1) + isk
                            continue
                        if module == 18:
                            isk = (isk * .2) + isk
                death = False
                if possible_npc is not False:
                    death = await self.weighted_choice(
                        [(True, possible_npc), (False, survival + ((ship['defense'] * 11) + (ship['maneuver'] * 6) +
                                                                   (ship['attack'] * 8)) * defense_multi)])
                if death is True:
                    embed = make_embed(icon=self.bot.user.avatar)
                    embed.set_footer(icon_url=self.bot.user.avatar_url,
                                     text="Aura - EVE Text RPG")
                    ship_image = await game_functions.get_ship_image(ship_id)
                    embed.set_thumbnail(url="{}".format(ship_image))
                    embed.add_field(name="Killmail",
                                    value="**Region** - {}\n\n"
                                          "**Loser**\n"
                                          "**{}** flying a {} was killed while belt mining.".format(region_name,
                                                                                                    user.display_name,
                                                                                                    ship['name']))
                    await self.add_loss(miner)
                    await user.send(embed=embed)
                    await self.send_global(embed, True)
                    return await self.destroy_ship(miner)

                xp_gained = await self.weighted_choice([(1, 35), (2, 15), (0, 15)])
                await self.add_xp(miner, xp_gained)
                await self.add_isk(miner, isk * multiplier)

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

    async def process_ganks(self):
        sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 4 '''
        roamers = await db.select(sql)
        if roamers is None or len(roamers) is 0:
            return
        for roamer in roamers:
            region_id = int(roamer[4])
            sql = ''' SELECT * FROM eve_rpg_players WHERE `task` != 1 AND `region` = (?) AND `player_id` != (?) '''
            values = (region_id, roamer[2])
            potential_targets = await db.select_var(sql, values)
            for target in potential_targets:
                target_aggression = 5
                if 1 < int(target[6]) < 5:
                    target_aggression = 45
                conflict = await self.weighted_choice([(True, target_aggression), (False, 65), (None, 45)])
                if conflict is None:
                    break
                elif conflict is True:
                    await self.solo_combat(roamer, target, True)
                    break

    async def solo_combat(self, attacker, defender, concord=False):
        attacker_ship = ast.literal_eval(attacker[14])
        attacker_ship_id = attacker_ship['ship_type']
        defender_ship = ast.literal_eval(defender[14])
        defender_ship_id = defender_ship['ship_type']
        attacker_attack, attacker_defense, attacker_maneuver, attacker_tracking = \
            await game_functions.get_combat_attributes(attacker, attacker_ship_id)
        defender_attack, defender_defense, defender_maneuver, defender_tracking = \
            await game_functions.get_combat_attributes(defender, defender_ship_id)
        tracking_one = 1
        if attacker_tracking < defender_maneuver:
            tracking_one = 0.8
        tracking_two = 1
        if defender_tracking < attacker_maneuver:
            tracking_two = 0.8
        pve_disadvantage = 0
        if 5 < int(defender[6]) < 11 or defender[6] == 10:
            pve_disadvantage = 2
        player_one_weight = (((attacker[8] + 1) * 0.5) + (attacker_attack - (defender_defense / 2))) * tracking_one
        player_two_weight = ((((defender[8] + 1) * 0.5) + (defender_attack -
                                                           (attacker_defense / 2))) * tracking_two) - pve_disadvantage
        winner = await self.weighted_choice([(attacker, player_one_weight), (defender, player_two_weight)])
        loser = attacker
        winner_catch = defender_attack / 2 + defender_tracking
        loser_escape = attacker_defense / 2 + attacker_maneuver
        winner_dies = False
        loser_dies = False
        if concord is True:
            loser_dies = True
        if winner is attacker:
            loser_dies = False
            if concord is True:
                winner_dies = True
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
        winner_ship_obj = ast.literal_eval(winner[14])
        winner_ship = await game_functions.get_ship_name(int(winner_ship_obj['ship_type']))
        winner_task = await game_functions.get_task(int(winner[6]))
        loser_ship_obj = ast.literal_eval(loser[14])
        loser_ship = await game_functions.get_ship_name(int(loser_ship_obj['ship_type']))
        loser_task = await game_functions.get_task(int(loser[6]))
        loser_modules = ''
        loser_modules_array = []
        dropped_mods = []
        if loser[12] is not None:
            modules = ast.literal_eval(loser[12])
            for module in modules:
                module_item = await game_functions.get_module(module)
                dropped = await self.weighted_choice([(True, 50), (False, 50)])
                module_drop = ''
                if dropped is True:
                    dropped_mods.append(module)
                    module_drop = ' **Module Dropped**'
                loser_modules_array.append('{} {}'.format(module_item['name'], module_drop))
            loser_module_list = '\n'.join(loser_modules_array)
            loser_modules = '\n\n__Modules Lost__\n{}'.format(loser_module_list)
        xp_gained = await self.weighted_choice([(5, 45), (15, 25), (27, 15)])
        if escape is False:
            embed = make_embed(icon=self.bot.user.avatar)
            embed.set_footer(icon_url=self.bot.user.avatar_url,
                             text="Aura - EVE Text RPG")
            ship_image = await game_functions.get_ship_image(loser_ship_obj['ship_type'])
            embed.set_thumbnail(url="{}".format(ship_image))
            embed.add_field(name="Killmail",
                            value="**Region** - {}\n\n"
                                  "**Loser**\n"
                                  "**{}** flying a {} was killed while they were {}.{}\n\n"
                                  "**Killer**\n"
                                  "**{}** flying a {} while {}.\n\n".format(region_name, loser_name, loser_ship,
                                                                            loser_task, loser_modules,
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
            if winner_dies is True:
                embed = make_embed(icon=self.bot.user.avatar)
                embed.set_footer(icon_url=self.bot.user.avatar_url,
                                 text="Aura - EVE Text RPG")
                ship_image = await game_functions.get_ship_image(loser_ship_obj['ship_type'])
                embed.set_thumbnail(url="{}".format(ship_image))
                embed.add_field(name="Killmail",
                                value="**Region** - {}\n\n"
                                      "**Loser**\n"
                                      "**{}** flying a {} was killed while they were {}.\n\n"
                                      "**Final Blow**\n"
                                      "Concord\n\n"
                                      "**Other Attackers**\n"
                                      "**{}** flying a {}".format(region_name, winner_name, winner_ship, winner_task,
                                                                  loser_name, loser_ship))
                await winner_user.send(embed=embed)
                await loser_user.send(embed=embed)
                await self.send_global(embed, True)
                await self.add_loss(winner)
                await self.add_kill(loser)
                await self.destroy_ship(winner)
                await self.add_xp(loser, xp_gained)
            else:
                if len(dropped_mods) > 0:
                    for mod in dropped_mods:
                        await self.give_mod(winner, mod)
                await self.give_pvp_loot(winner)
        else:
            winner_user = self.bot.get_user(winner[2])
            loser_user = self.bot.get_user(loser[2])
            if winner_dies is False:
                await winner_user.send(
                    '**PVP** - Combat between you and a {} flown by {}, they nearly died to your {} but '
                    'managed to warp off and dock.'.format(loser_ship, loser_name, winner_ship))
            else:
                embed = make_embed(icon=self.bot.user.avatar)
                embed.set_footer(icon_url=self.bot.user.avatar_url,
                                 text="Aura - EVE Text RPG")
                ship_image = await game_functions.get_ship_image(winner_ship_obj['ship_type'])
                embed.set_thumbnail(url="{}".format(ship_image))
                embed.add_field(name="Killmail",
                                value="**Region** - {}\n\n"
                                      "**Loser**\n"
                                      "**{}** flying a {} was killed while they were {}.\n\n"
                                      "**Final Blow**\n"
                                      "Concord\n\n"
                                      "**Other Attackers**\n"
                                      "**{}** flying a {}".format(region_name, winner_name, winner_ship, winner_task,
                                                                  loser_name, loser_ship))
                try:
                    await winner_user.send(embed=embed)
                except Exception:
                    self.logger.error('User {} message error'.format(winner_user.id))
                try:
                    await loser_user.send(embed=embed)
                except Exception:
                    self.logger.error('User {} message error'.format(loser_user.id))
                await self.send_global(embed, True)
                await self.add_loss(winner)
                await self.add_kill(loser)
                await self.destroy_ship(winner)
                await self.add_xp(winner, xp_gained)

            if loser_dies is False:
                await loser_user.send('**PVP** - Combat between you and a {} flown by {}, you nearly lost your {} but '
                                      'managed to break tackle and dock.'.format(winner_ship, winner_name, loser_ship))
            else:
                embed = make_embed(icon=self.bot.user.avatar)
                embed.set_footer(icon_url=self.bot.user.avatar_url,
                                 text="Aura - EVE Text RPG")
                ship_image = await game_functions.get_ship_image(loser_ship_obj['ship_type'])
                embed.set_thumbnail(url="{}".format(ship_image))
                embed.add_field(name="Killmail",
                                value="**Region** - {}\n\n"
                                      "**Loser**\n"
                                      "**{}** flying a {} was killed while they were {}.{}\n\n"
                                      "**Final Blow**\n"
                                      "Concord\n\n"
                                      "**Other Attackers**\n"
                                      "**{}** flying a {}".format(region_name, loser_name, loser_ship, loser_task,
                                                                  loser_modules, winner_name, winner_ship))
                await winner_user.send(embed=embed)
                await loser_user.send(embed=embed)
                await self.send_global(embed, True)
                await self.add_loss(loser)
                await self.add_kill(winner)
                if len(dropped_mods) > 0:
                    for mod in dropped_mods:
                        await self.give_mod(winner, mod)
                await self.give_pvp_loot(winner)
                await self.destroy_ship(loser)
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
                continue
            if embed is False:
                await channel.send(message)
                continue
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
        if player[9] + xp_gained < 100 * player[8]:
            sql = ''' UPDATE eve_rpg_players
                    SET xp = (?)
                    WHERE
                        player_id = (?); '''
            values = (player[9] + xp_gained, player[2],)
        else:
            sql = ''' UPDATE eve_rpg_players
                    SET level = (?),
                        xp = (?)
                    WHERE
                        player_id = (?); '''
            values = (player[8] + 1, 0, player[2],)
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
                SET kills = (?),
                    ship = (?)
                WHERE
                    player_id = (?); '''
        killer_ship = ast.literal_eval(player[14])
        if 'kill_marks' not in killer_ship:
            killer_ship['kill_marks'] = 1
        else:
            killer_ship['kill_marks'] += 1
        values = (int(player[10]) + 1, str(killer_ship), player[2],)
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
        if player[3] == 1:
            ship_id = 1
        elif player[3] == 2:
            ship_id = 2
        elif player[3] == 3:
            ship_id = 3
        elif player[3] == 4:
            ship_id = 4
        elif player[3] == 99:
            ship_id = 5
        lost_ship = ast.literal_eval(player[14])
        new_id = await game_functions.create_unique_id()
        ship = {'id': new_id, 'ship_type': ship_id}
        sql = ''' UPDATE eve_rpg_players
                SET ship = (?),
                    modules = NULL,
                    region = (?),
                    task = 1
                WHERE
                    player_id = (?); '''
        values = (str(ship), player[18], player[2],)
        await db.execute_sql(sql, values)
        if 'insured' in lost_ship:
            channel = self.bot.get_user(player[2])
            insurance_payout = '{0:,.2f}'.format(float(lost_ship['insurance_payout']))
            if player[6] == 4:
                return await channel.send(
                    '**Insurance DENIED** We regret to inform you that because you were performing'
                    ' a criminal act at the time of your death we will be keeping your payout of '
                    '{} ISK.'.format(insurance_payout))
            lost_ship_details = await game_functions.get_ship(lost_ship['ship_type'])
            await channel.send('**Insurance Payout Received**\n\nThe loss of your {} was covered by insurance, {} ISK '
                               'has been deposited into your account.'.format(lost_ship_details['name'],
                                                                              insurance_payout))
            sql = ''' UPDATE eve_rpg_players
                    SET isk = (?)
                    WHERE
                        player_id = (?); '''
            new_isk = float(player[5]) + float(lost_ship['insurance_payout'])
            values = (int(float(new_isk)), player[2],)
            await db.execute_sql(sql, values)

    async def give_mod(self, player, mod):
        ship = ast.literal_eval(player[14])
        if 'module_cargo_bay' in ship:
            ship['module_cargo_bay'].append(mod)
        else:
            ship['module_cargo_bay'] = [mod]
        sql = ''' UPDATE eve_rpg_players
                SET ship = (?)
                WHERE
                    player_id = (?); '''
        values = (str(ship), player[2],)
        await db.execute_sql(sql, values)

    async def give_pvp_loot(self, player):
        ship = ast.literal_eval(player[14])
        tier_1_amount = random.randint(1, 50)
        tier_1 = await self.weighted_choice([(True, 90), (False, 10)])
        tier_1_text = ''
        tier_2_amount = random.randint(1, 10)
        tier_2 = await self.weighted_choice([(True, 55), (False, 45)])
        tier_2_text = ''
        tier_3_amount = random.randint(1, 3)
        tier_3 = await self.weighted_choice([(True, 2), (False, 98)])
        tier_3_text = ''
        if 'component_cargo_bay' in ship:
            loot = ship['component_cargo_bay']
        else:
            loot = []
        if tier_1 is True:
            loot_id = await game_functions.create_unique_id()
            component = await game_functions.get_component(1)
            tier_1_loot = {'type_id': 1, 'id': loot_id, 'amount': tier_1_amount}
            loot.append(tier_1_loot)
            tier_1_text = '{}x {}\n'.format(tier_1_amount, component['name'])
        if tier_2 is True:
            loot_id = await game_functions.create_unique_id()
            loot_type = await self.weighted_choice([(2, 35), (3, 65)])
            component = await game_functions.get_component(loot_type)
            tier_2_loot = {'type_id': loot_type, 'id': loot_id, 'amount': tier_2_amount}
            loot.append(tier_2_loot)
            tier_1_text = '{}x {}\n'.format(tier_2_amount, component['name'])
        if tier_3 is True:
            loot_id = await game_functions.create_unique_id()
            loot_type = await self.weighted_choice([(4, 65), (5, 35)])
            component = await game_functions.get_component(loot_type)
            tier_3_loot = {'type_id': loot_type, 'id': loot_id, 'amount': tier_3_amount}
            loot.append(tier_3_loot)
            tier_1_text = '{}x {}\n'.format(tier_3_amount, component['name'])
        if tier_1 is True or tier_2 is True or tier_3 is True:
            channel = self.bot.get_user(player[2])
            await channel.send('**Ship Component Salvage Received**\n{}{}{}\n\n*Salvage stored in your ships component'
                               ' cargo bay.'.format(tier_1_text, tier_2_text, tier_3_text))
            ship['component_cargo_bay'] = loot
            sql = ''' UPDATE eve_rpg_players
                    SET ship = (?)
                    WHERE
                        player_id = (?); '''
            values = (str(ship), player[2],)
            await db.execute_sql(sql, values)
