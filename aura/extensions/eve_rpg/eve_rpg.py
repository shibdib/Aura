import ast
import asyncio
import datetime
import itertools
import random

from aura.lib import db
from aura.lib import game_assets
from aura.lib import game_functions
from aura.utils import make_embed


async def process_region_stats():
    current_tick = await game_functions.get_tick()
    if current_tick % 300 == 0:
        sql = "SELECT * FROM region_info"
        regions = await db.select(sql)
        for region in regions:
            current_hourly_npc = region[7]
            current_hourly_player = region[9]
            sql = ''' UPDATE region_info
                    SET npc_kills_previous_hour = (?),
                        player_kills_previous_hour = (?),
                        npc_kills_hour = 0,
                        player_kills_hour = 0
                    WHERE
                        region_id = (?); '''
            values = (current_hourly_npc, current_hourly_player, region[1],)
            await db.execute_sql(sql, values)
    if current_tick % 7200 == 0:
        sql = "SELECT * FROM region_info"
        regions = await db.select(sql)
        for region in regions:
            current_day_npc = region[8]
            current_day_player = region[10]
            sql = ''' UPDATE region_info
                    SET npc_kills_previous_day = (?),
                        player_kills_previous_day = (?),
                        npc_kills_day = 0,
                        player_kills_day = 0
                    WHERE
                        region_id = (?); '''
            values = (current_day_npc, current_day_player, region[1],)
            await db.execute_sql(sql, values)


async def weighted_choice(items):
    """items is a list of tuples in the form (item, weight)"""
    weight_total = sum((item[1] for item in items))
    n = random.uniform(0, weight_total)
    for item, weight in items:
        if n < weight:
            return item
        n = n - weight
    return item


async def give_mod(player, mods):
    player = await game_functions.refresh_player(player)
    ship = ast.literal_eval(player[14])
    for mod in mods:
        if 'module_cargo_bay' in ship:
            ship['module_cargo_bay'].append(mod)
        else:
            ship['module_cargo_bay'] = [mod]
    new_ship = str(ship)
    sql = ''' UPDATE eve_rpg_players
            SET ship = (?)
            WHERE
                player_id = (?); '''
    values = (new_ship, player[2],)
    return await db.execute_sql(sql, values)


async def add_combat_timer(player):
    player = await game_functions.refresh_player(player)
    sql = ''' UPDATE eve_rpg_players
            SET combat_timer = (?)
            WHERE
                player_id = (?); '''
    values = (5, player[2],)
    return await db.execute_sql(sql, values)


async def add_loss(player):
    player = await game_functions.refresh_player(player)
    sql = ''' UPDATE eve_rpg_players
            SET losses = (?)
            WHERE
                player_id = (?); '''
    values = (int(player[11]) + 1, player[2],)
    return await db.execute_sql(sql, values)


async def add_kill(player, mods):
    player = await game_functions.refresh_player(player)
    sql = ''' UPDATE eve_rpg_players
            SET kills=?,
                ship=?
            WHERE
                player_id=?; '''
    killer_ship = ast.literal_eval(player[14])
    if 'kill_marks' not in killer_ship:
        killer_ship['kill_marks'] = 1
    else:
        killer_ship['kill_marks'] += 1
    if mods is not None:
        for mod in mods:
            if 'module_cargo_bay' in killer_ship:
                killer_ship['module_cargo_bay'].append(mod)
            else:
                killer_ship['module_cargo_bay'] = [mod]
    values = (int(player[10]) + 1, str(killer_ship), player[2],)
    return await db.execute_sql(sql, values)


async def update_journal(player, isk, entry):
    player = await game_functions.refresh_player(player)
    utc = datetime.datetime.utcnow()
    time = utc.strftime("%H:%M:%S")
    if player[20] is not None:
        journal = ast.literal_eval(player[20])
        if len(journal) == 10:
            journal.pop(0)
        transaction = {'isk': isk, 'type': entry, 'time': time}
        journal.append(transaction)
    else:
        transaction = {'isk': isk, 'type': entry, 'time': time}
        journal = [transaction]
    sql = ''' UPDATE eve_rpg_players
            SET wallet_journal = (?)
            WHERE
                player_id = (?); '''
    values = (str(journal), player[2],)
    return await db.execute_sql(sql, values)


async def add_isk(player, isk):
    player = await game_functions.refresh_player(player)
    sql = ''' UPDATE eve_rpg_players
            SET isk = (?)
            WHERE
                player_id = (?); '''
    values = (int(player[5]) + isk, player[2],)
    return await db.execute_sql(sql, values)


async def add_xp(player, xp_gained):
    player = await game_functions.refresh_player(player)
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
    return await db.execute_sql(sql, values)


class EveRpg:
    def __init__(self, bot):
        self.bot = bot
        self.ongoing_fleet_fights = {}
        self.session = bot.session
        self.config = bot.config
        self.logger = bot.logger
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.tick_loop())
        self.active_sites = 0

    async def tick_loop(self):
        await self.bot.wait_until_ready()
        await self.initial_checks()
        while not self.bot.is_closed():
            try:
                await self.process_travel()
                asyncio.ensure_future(game_functions.tick_count())
                asyncio.ensure_future(game_functions.combat_timer_management())
                asyncio.ensure_future(self.process_special_regions())
                asyncio.ensure_future(process_region_stats())
                asyncio.ensure_future(self.process_belt_ratting())
                asyncio.ensure_future(self.process_missions())
                asyncio.ensure_future(self.process_belt_mining())
                asyncio.ensure_future(self.process_anomaly_mining())
                asyncio.ensure_future(self.process_anomaly_ratting())
                asyncio.ensure_future(self.process_ongoing_fleet_fights())
                asyncio.ensure_future(self.process_roams())
                asyncio.ensure_future(self.process_ganks())
                asyncio.ensure_future(self.process_users())
                await asyncio.sleep(12)
            except Exception:
                self.logger.exception('ERROR:')
                await asyncio.sleep(5)

    async def initial_checks(self):
        sql = "SELECT * FROM eve_rpg_players"
        players = await db.select(sql)
        for player in players:
            user = self.bot.get_user(player[2])
            if user is None:
                await self.remove_bad_user(player[2])
                continue
        # Make sure regions are in the db
        for key, region in game_assets.regions.items():
            sql = "SELECT * FROM region_info WHERE `region_id` = (?)"
            values = (key,)
            region = await db.select_var(sql, values)
            if len(region) == 0:
                sec_status = await game_functions.get_region_security(key)
                sql = ''' REPLACE INTO region_info(region_id,region_security)
                          VALUES(?,?) '''
                values = (key, sec_status)
                await db.execute_sql(sql, values)
            sql = "SELECT * FROM region_market WHERE `region_id` = (?)"
            values = (key,)
            region = await db.select_var(sql, values)
            if len(region) == 0:
                sql = ''' REPLACE INTO region_market(region_id)
                          VALUES(?) '''
                values = (key,)
                await db.execute_sql(sql, values)

    async def process_users(self):
        current_tick = await game_functions.get_tick()
        if current_tick % 100 == 0:
            sql = "SELECT * FROM eve_rpg_players"
            players = await db.select(sql)
            for player in players:
                user = self.bot.get_user(player[2])
                if user is None:
                    await self.remove_bad_user(player[2])
                    continue

    async def process_special_regions(self):
        sql = "SELECT * FROM region_info WHERE `pirate_anomaly` > 0 AND `region_security` != 'High'"
        active_pirate_anomalies = await db.select(sql)
        current_tick = await game_functions.get_tick()
        if len(active_pirate_anomalies) < 8:
            if len(active_pirate_anomalies) < 8:
                sql = "SELECT * FROM region_info WHERE `pirate_anomaly` == 0 AND `region_security` != 'High'"
                potential_pirate_anomalies = await db.select(sql)
                random.shuffle(potential_pirate_anomalies)
                trimmed_list = potential_pirate_anomalies[:8 - len(active_pirate_anomalies)]
                for new_anomaly in trimmed_list:
                    sql = ''' UPDATE region_info
                            SET pirate_anomaly = 1
                            WHERE
                                region_id = (?); '''
                    values = (new_anomaly[1],)
                    await db.execute_sql(sql, values)
        elif current_tick % 300 == 0:
            reset_amount = random.randint(1, 8)
            random.shuffle(active_pirate_anomalies)
            trimmed_list = active_pirate_anomalies[:reset_amount]
            for reset_anomaly in trimmed_list:
                sql = ''' UPDATE region_info
                        SET pirate_anomaly = 0
                        WHERE
                            region_id = (?); '''
                values = (reset_anomaly[1],)
                await db.execute_sql(sql, values)
                sql = "SELECT * FROM eve_rpg_players WHERE `region` == (?) AND (`task` == 7 OR `task` == 34)"
                values = (reset_anomaly[1],)
                anomaly_runners = await db.select_var(sql, values)
                if len(anomaly_runners) > 0:
                    for runner in anomaly_runners:
                        sql = ''' UPDATE eve_rpg_players
                                SET task = 21
                                WHERE
                                    id = (?); '''
                        values = (runner[0],)
                        await db.execute_sql(sql, values)
                        player = self.bot.get_user(runner[2])
                        await player.send('**Notice** The pirates have fled the system, the anomaly you were in '
                                          'has been defeated and you are now floating in space.')
        sql = "SELECT * FROM region_info WHERE `mining_anomaly` > 0 AND `region_security` != 'High'"
        active_mining_anomalies = await db.select(sql)
        if len(active_mining_anomalies) < 8:
            if len(active_mining_anomalies) < 8:
                sql = "SELECT * FROM region_info WHERE `mining_anomaly` == 0 AND `region_security` != 'High'"
                potential_pirate_anomalies = await db.select(sql)
                random.shuffle(potential_pirate_anomalies)
                trimmed_list = potential_pirate_anomalies[:8 - len(active_mining_anomalies)]
                for new_anomaly in trimmed_list:
                    sql = ''' UPDATE region_info
                            SET mining_anomaly = 1
                            WHERE
                                region_id = (?); '''
                    values = (new_anomaly[1],)
                    await db.execute_sql(sql, values)
        elif current_tick % 300 == 0:
            reset_amount = random.randint(1, 8)
            random.shuffle(active_mining_anomalies)
            trimmed_list = active_mining_anomalies[:reset_amount]
            for reset_anomaly in trimmed_list:
                sql = ''' UPDATE region_info
                        SET mining_anomaly = 0
                        WHERE
                            region_id = (?); '''
                values = (reset_anomaly[1],)
                await db.execute_sql(sql, values)
                sql = "SELECT * FROM eve_rpg_players WHERE `region` == (?) AND (`task` == 11 OR `task` == 35)"
                values = (reset_anomaly[1],)
                anomaly_runners = await db.select_var(sql, values)
                if len(anomaly_runners) > 0:
                    for runner in anomaly_runners:
                        sql = ''' UPDATE eve_rpg_players
                                SET task = 21
                                WHERE
                                    id = (?); '''
                        values = (runner[0],)
                        await db.execute_sql(sql, values)
                        player = self.bot.get_user(runner[2])
                        await player.send(
                            '**Notice** The asteroid have been mined, the anomaly you were once in is now '
                            'nothing more than a dust cloud.')

    async def process_ongoing_fleet_fights(self):
        if len(self.ongoing_fleet_fights) > 0:
            for fight in self.ongoing_fleet_fights:
                await self.fleet_versus_fleet(fight['attacker'], fight['defender'], fight['region'], fight['damaged'])

    async def process_travel(self):
        sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 20 '''
        travelers = await db.select(sql)
        if travelers is None or len(travelers) is 0:
            return
        for traveler in travelers:
            region_id = int(traveler[4])
            destination_id = int(traveler[17])
            sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 3 AND (`region` = (?) OR `region` = (?)) '''
            values = (region_id, destination_id,)
            campers = await db.select_var(sql, values)
            traveler_ship = ast.literal_eval(traveler[14])
            defender_ship_id = traveler_ship['ship_type']
            defender_attack, defender_defense, defender_maneuver, defender_tracking = \
                await game_functions.get_combat_attributes(traveler, defender_ship_id)
            if len(campers) is not 0:
                for camper in campers:
                    # Corp check
                    if camper[23] is not None:
                        corp_info = await game_functions.get_user_corp(camper[23])
                        corp_array = ast.literal_eval(corp_info[7])
                        if traveler[0] in corp_array:
                            continue
                    # Blue check
                    if camper[21] is not None:
                        blue_array = ast.literal_eval(camper[21])
                        if traveler[0] in blue_array:
                            continue
                    # Fleet check
                    if camper[16] is not None and camper[16] != 0:
                        sql = ''' SELECT * FROM fleet_info WHERE `fleet_id` = (?) '''
                        values = (camper[16],)
                        fleet_info = await db.select_var(sql, values)
                        fleet_array = ast.literal_eval(fleet_info[0][3])
                        if traveler[0] in fleet_array:
                            continue
                    conflict = await weighted_choice([(True, 55 - defender_maneuver), (False, 55)])
                    if conflict is True:
                        camper_fleet = False
                        traveler_fleet = False
                        if camper[16] is not None and camper[16] != 0:
                            camper_fleet = True
                        if traveler[16] is not None and traveler[16] != 0:
                            traveler_fleet = True
                        if traveler_fleet is False and camper_fleet is False:
                            await self.solo_combat(camper, traveler)
                        elif traveler_fleet is False and camper_fleet is True:
                            sql = ''' SELECT * FROM fleet_info WHERE `fleet_id` = (?) '''
                            values = (camper[16],)
                            fleet_info = await db.select_var(sql, values)
                            await self.fleet_versus_player(fleet_info[0], traveler, region_id)
                        elif camper_fleet is False and traveler_fleet is True:
                            sql = ''' SELECT * FROM fleet_info WHERE `fleet_id` = (?) '''
                            values = (traveler[16],)
                            fleet_info = await db.select_var(sql, values)
                            await self.fleet_versus_player(fleet_info[0], camper, region_id)
                        elif camper_fleet is True and traveler_fleet is True:
                            sql = ''' SELECT * FROM fleet_info WHERE `fleet_id` = (?) '''
                            values = (traveler[16],)
                            fleet_one_info = await db.select_var(sql, values)
                            sql = ''' SELECT * FROM fleet_info WHERE `fleet_id` = (?) '''
                            values = (camper[16],)
                            fleet_two_info = await db.select_var(sql, values)
                            await self.fleet_versus_fleet(fleet_one_info[0], fleet_two_info[0], region_id)
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
            region_info = await game_functions.get_region_info(destination_id)
            anomaly_text = ''
            if region_info[4] != 0:
                anomaly_text = "*Pirate Anomalies Present In This Region*\n\n"
            if region_info[5] != 0:
                anomaly_text = "*Rich Mining Anomalies Present In This Region*\n\n"
            if region_info[5] != 0 and region_info[4] != 0:
                anomaly_text = "*Pirate Anomalies Present In This Region*\n*Rich Ore Anomalies Present In This Region*\n\n"
            pve_kills_hour, pve_kills_day, pvp_kills_hour, pvp_kills_day, pve_kills_last_hour, pve_kills_yesterday, pvp_kills_last_hour, pvp_kills_yesterday = await game_functions.get_region_kill_info(
                destination_id)
            await player.send('**You have arrived in {}**\n\n{}'
                              'Local Count - {}\n'
                              'NPC Kills Last Hour/Prior Hour - {}/{}\n'
                              'Player Kills Last Hour/Prior Hour - {}/{}'.format(destination_name, anomaly_text,
                                                                                 len(local_players),
                                                                                 pve_kills_hour, pve_kills_last_hour,
                                                                                 pvp_kills_hour, pvp_kills_last_hour))

    async def process_belt_ratting(self):
        sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 6 '''
        ratters = await db.select(sql)
        if ratters is None or len(ratters) is 0:
            return
        for ratter in ratters:
            region_id = int(ratter[4])
            region_security = await game_functions.get_region_security(region_id)
            sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 6 AND `region` = (?) '''
            values = (region_id,)
            system_ratters = await db.select_var(sql, values)
            npc = 45
            isk_multi = 0.25
            if region_security == 'Low':
                npc = 55
                isk_multi = 0.5
            elif region_security == 'Null':
                npc = 75
                isk_multi = 0.65
            #  PVE Rolls
            encounter = await weighted_choice(
                [(True, npc / len(system_ratters)), (False, 100 - npc + 1)])
            if encounter is True:
                await self.process_pve_combat(ratter, isk_multi)

    async def process_anomaly_ratting(self):
        sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 7 '''
        ratters = await db.select(sql)
        if ratters is None or len(ratters) is 0:
            return
        for ratter in ratters:
            region_id = int(ratter[4])
            region_security = await game_functions.get_region_security(region_id)
            sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 7 AND `region` = (?) '''
            values = (region_id,)
            system_ratters = await db.select_var(sql, values)
            npc = 35
            if region_security == 'Low':
                npc = 55
            elif region_security == 'Null':
                npc = 75
            #  PVE Rolls
            encounter = await weighted_choice(
                [(True, npc / len(system_ratters)), (False, 100 - npc + 1)])
            if encounter is True:
                await self.process_pve_combat(ratter)

    async def process_belt_mining(self):
        sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 10 '''
        miners = await db.select(sql)
        if miners is None or len(miners) is 0:
            return
        for miner in miners:
            region_id = int(miner[4])
            region_security = await game_functions.get_region_security(region_id)
            sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 10 AND `region` = (?) '''
            values = (region_id,)
            belt_miners = await db.select_var(sql, values)
            isk = random.randint(100, 750)
            possible_npc = False
            ore = 50
            if region_security == 'Low':
                ore = 75
                possible_npc = 2
                isk = random.randint(2500, 8500)
            elif region_security == 'Null':
                ore = 90
                possible_npc = 4
                isk = random.randint(8000, 22450)
            find_ore = await weighted_choice(
                [(True, ore / len(belt_miners)), (False, 100 - (ore / len(belt_miners)))])
            if find_ore is False:
                continue
            else:
                if possible_npc is not False:
                    encounter = await weighted_choice([(True, possible_npc), (False, 100 - possible_npc)])
                    if encounter is True:
                        await self.process_pve_combat(miner)
                #  Ship multi
                miner_ship = ast.literal_eval(miner[14])
                ship_id = miner_ship['ship_type']
                ship = await game_functions.get_ship(ship_id)
                multiplier = 1
                if ship['class'] == 21:
                    multiplier = 2.25
                if ship['id'] == 80:
                    multiplier = 4
                if ship['id'] == 81:
                    multiplier = 8
                if ship['id'] == 90:
                    multiplier = 6
                if ship['id'] == 91:
                    multiplier = 12
                if miner[12] is not None:
                    modules = ast.literal_eval(miner[12])
                    for module in modules:
                        if module == 17:
                            isk = (isk * .1) + isk
                            continue
                        if module == 18:
                            isk = (isk * .2) + isk
                            continue
                        if module == 121:
                            isk = (isk * .05) + isk
                            continue
                        if module == 122:
                            isk = (isk * .1) + isk
                xp_gained = await weighted_choice([(1, 35), (2, 15), (0, 15)])
                await add_xp(miner, xp_gained)
                await add_isk(miner, isk * multiplier)
                await update_journal(miner, isk * multiplier, 'Belt Mining')

    async def process_anomaly_mining(self):
        sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 11 '''
        miners = await db.select(sql)
        if miners is None or len(miners) is 0:
            return
        for miner in miners:
            region_id = int(miner[4])
            region_security = await game_functions.get_region_security(region_id)
            sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 11 AND `region` = (?) '''
            values = (region_id,)
            belt_miners = await db.select_var(sql, values)
            isk = random.randint(100, 750)
            possible_npc = False
            ore = 50
            if region_security == 'Low':
                ore = 99
                possible_npc = 4
                isk = random.randint(12000, 19500)
            elif region_security == 'Null':
                ore = 99
                possible_npc = 8
                isk = random.randint(18000, 65000)
            find_ore = await weighted_choice(
                [(True, ore / len(belt_miners)), (False, 100 - (ore / len(belt_miners)))])
            if find_ore is False:
                continue
            else:
                if possible_npc is not False:
                    encounter = await weighted_choice([(True, possible_npc), (False, 100 - possible_npc)])
                    if encounter is True:
                        await self.process_pve_combat(miner)
                #  Ship multi
                miner_ship = ast.literal_eval(miner[14])
                ship_id = miner_ship['ship_type']
                ship = await game_functions.get_ship(ship_id)
                multiplier = 1
                if ship['class'] == 21:
                    multiplier = 2.25
                if ship['id'] == 80:
                    multiplier = 4
                if ship['id'] == 81:
                    multiplier = 8
                if ship['id'] == 90:
                    multiplier = 6
                if ship['id'] == 91:
                    multiplier = 12
                if miner[12] is not None:
                    modules = ast.literal_eval(miner[12])
                    for module in modules:
                        if module == 17:
                            isk = (isk * .1) + isk
                            continue
                        if module == 18:
                            isk = (isk * .2) + isk
                            continue
                        if module == 121:
                            isk = (isk * .05) + isk
                            continue
                        if module == 122:
                            isk = (isk * .1) + isk
                xp_gained = await weighted_choice([(1, 35), (2, 15), (0, 15)])
                await add_xp(miner, xp_gained)
                await add_isk(miner, isk * multiplier)
                await update_journal(miner, isk * multiplier, 'Anomaly Mining')

    async def process_missions(self):
        sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 9 '''
        mission_runners = await db.select(sql)
        if mission_runners is None or len(mission_runners) is 0:
            return
        for mission_runner in mission_runners:
            if mission_runner[22] is None:
                sql = ''' UPDATE eve_rpg_players
                        SET task = 10
                        WHERE
                            player_id = (?); '''
                values = (mission_runner[2],)
                return await db.execute_sql(sql, values)
            mission_details = ast.literal_eval(mission_runner[22])
            isk = mission_details['reward']
            #  PVE Rolls
            complete_mission = await weighted_choice([(True, 15), (False, 30 * mission_details['level'])])
            enounter = await weighted_choice([(True, 70), (False, 30)])
            if enounter is True and complete_mission is False:
                await self.process_pve_combat(mission_runner, 1, mission_details['level'])
            else:
                if complete_mission is False:
                    continue
                xp_gained = await weighted_choice([(1 * mission_details['level'], 35),
                                                   (3 * mission_details['level'], 15),
                                                   (0, 15)])
                await add_xp(mission_runner, xp_gained)
                await add_isk(mission_runner, isk)
                loot_chance = 4 * mission_details['level']
                await self.pve_loot(mission_runner, loot_chance, True)
                await update_journal(mission_runner, isk, 'Mission Reward')
                embed = make_embed(icon=self.bot.user.avatar)
                embed.set_footer(icon_url=self.bot.user.avatar_url,
                                 text="Aura - EVE Text RPG")
                embed.add_field(name="Mission Completed",
                                value="{}\n\n"
                                      "Reward: {} ISK\n".format(mission_details['completion'],
                                                                '{0:,.2f}'.format(float(mission_details['reward']))))
                mission_runner = await game_functions.refresh_player(mission_runner)
                player = self.bot.get_user(mission_runner[2])
                await player.send(embed=embed)
                sql = ''' UPDATE eve_rpg_players
                        SET task = 21,
                            mission_details = (?)
                        WHERE
                            player_id = (?); '''
                values = (None, mission_runner[2],)
                await db.execute_sql(sql, values)

    async def process_pve_combat(self, player, isk_multi=1, mission=False):
        region_id = int(player[4])
        player_user = self.bot.get_user(player[2])
        player_task = await game_functions.get_task(int(player[6]))
        player_ship = ast.literal_eval(player[14])
        ship_id = player_ship['ship_type']
        player_ship_info = await game_functions.get_ship(ship_id)
        player_attack, player_defense, player_maneuver, player_tracking = \
            await game_functions.get_combat_attributes(player, ship_id)
        payout_array = [player]
        if player[16] is not None and player[16] != 0:
            payout_array = []
            sql = ''' SELECT * FROM fleet_info WHERE `fleet_id` = (?) '''
            values = (player[16],)
            fleet_info = await db.select_var(sql, values)
            fleet_array = ast.literal_eval(fleet_info[0][3])
            player_attack = 0
            for member_id in fleet_array:
                sql = ''' SELECT * FROM eve_rpg_players WHERE `id` = (?) '''
                values = (int(member_id),)
                member = await db.select_var(sql, values)
                if member[0][4] != region_id:
                    continue
                if member[0][6] != player[6] and int(player[6]) != 10:
                    continue
                payout_array.append(member[0])
                member_ship = ast.literal_eval(member[0][14])
                member_attack, member_defense, member_maneuver, member_tracking = \
                    await game_functions.get_combat_attributes(member[0], member_ship['ship_type'])
                player_attack += member_attack
        ship = await game_functions.get_ship(ship_id)
        region_security = await game_functions.get_region_security(region_id)
        officer = False
        if mission is not False:
            npc = await game_functions.get_npc(mission + 9)
        elif region_security == 'High':
            npc = await game_functions.get_npc(0)
        elif region_security == 'Low':
            npc = await game_functions.get_npc(1)
        else:
            officer = await weighted_choice([(True, 1), (False, 750)])
            if officer is False:
                npc = await game_functions.get_npc(2)
            else:
                npc = await game_functions.get_npc(20)
        escape_chance = player_defense / 2 + player_maneuver
        if player_maneuver == 0:
            escape_chance = 0
        npc_attack, npc_defense, npc_maneuver, npc_tracking = \
            await game_functions.get_combat_attributes(player, npc['id'], True)
        region_name = await game_functions.get_region(int(region_id))
        # Combat
        transversal = 1
        if (player_maneuver * 0.75) > npc_tracking + 1:
            transversal = (npc_tracking + 1) / (player_maneuver * 0.75)
        minimum_npc_damage = (npc_attack * transversal)
        maximum_npc_damage = npc_attack
        npc_triangular_medium = (maximum_npc_damage + minimum_npc_damage) / 4
        transversal = 1
        if (npc_maneuver * 0.75) > player_tracking + 1:
            transversal = (player_tracking + 1) / (npc_maneuver * 0.75)
        minimum_player_damage = (player_attack * transversal)
        maximum_player_damage = player_attack
        player_triangular_medium = (minimum_player_damage + maximum_player_damage) / 4
        player_hits, npc_hits = ship['hit_points'], npc['hit_points']
        round_counter = 1
        for x in range(125):
            player_defense = await game_functions.manage_regen(player, player_defense)
            npc_damage = round(random.triangular(minimum_npc_damage, maximum_npc_damage, npc_triangular_medium), 3)
            player_damage = round(
                random.triangular(minimum_player_damage, maximum_player_damage, player_triangular_medium), 3)
            if round_counter % 2 == 0:
                aggressor = False
            else:
                aggressor = player
            round_counter += 1
            if aggressor != player:
                if player_defense > 0:
                    if player_defense >= npc_damage:
                        player_defense -= npc_damage
                    else:
                        npc_damage -= player_defense
                        player_defense = 0
                        player_hits -= npc_damage
                else:
                    player_hits -= npc_damage
            else:
                if npc_defense > 0:
                    if npc_defense >= player_damage:
                        npc_defense -= player_damage
                    else:
                        player_damage -= npc_defense
                        npc_defense = 0
                        npc_hits -= player_damage
                else:
                    npc_hits -= player_damage
            if player_hits <= 0:
                break
            if npc_hits <= 0:
                for player in payout_array:
                    await game_functions.track_npc_kills(region_id)
                    await add_xp(player, random.randint(2, 10))
                    await add_isk(player, int(float((npc['isk'] * isk_multi))) / len(payout_array))
                    await update_journal(player, int(float((npc['isk'] * isk_multi))) / len(payout_array),
                                         '{} - {}'.format(player_task, npc['name']))
                if officer is True:
                    await self.pve_loot(player, 1, False, True)
                return
            if player_hits < ship['hit_points']:
                escape = await weighted_choice([(True, escape_chance), (False, 100 - escape_chance)])
                if escape is True:
                    await player_user.send(
                        '**PVE ESCAPE** - Combat between you and a {}, they nearly killed your {} but you '
                        'managed to warp off.'.format(npc['name'], player_ship_info['name']))
                    return
        if npc_hits > 0 and player_hits > 0:
            await player_user.send(
                '**PVE DISENGAGE** - Combat between you and a {}, has ended in a draw. You ended the battle '
                'with {} of {} hit points, while they ended with {} of {} hit points.'.format(
                    npc['name'], player_hits, ship['hit_points'], npc_hits,
                    npc['hit_points']))
            return
        module_value = 0
        loser_modules = ''
        cargo_modules = ''
        loser_modules_array = []
        cargo_modules_array = []
        loser_name = player_user.display_name
        if player[23] is not None:
            corp_info = await game_functions.get_user_corp(player[23])
            loser_name = '{} [{}]'.format(loser_name, corp_info[4])
        if player[12] is not None:
            modules = ast.literal_eval(player[12])
            for module in modules:
                module_item = await game_functions.get_module(module)
                module_value += module_item['isk']
                loser_modules_array.append('{}'.format(module_item['name']))
            loser_module_list = '\n'.join(loser_modules_array)
            loser_modules = '\n\n__Equipped Modules Lost__\n{}'.format(loser_module_list)
        if 'module_cargo_bay' in player_ship:
            modules = player_ship['module_cargo_bay']
            for module in modules:
                module_item = await game_functions.get_module(module)
                module_value += module_item['isk']
                cargo_modules_array.append('{}'.format(module_item['name']))
            cargo_module_list = '\n'.join(cargo_modules_array)
            cargo_modules = '\n\n__Cargo Lost__\n{}'.format(cargo_module_list)
        module_value += ship['isk']
        embed = make_embed(icon=self.bot.user.avatar)
        embed.set_footer(icon_url=self.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        ship_image = await game_functions.get_ship_image(ship_id)
        embed.set_thumbnail(url="{}".format(ship_image))
        embed.add_field(name="NPC Killmail",
                        value="**Region** - {}\n\n"
                              "__**Loser**__\n"
                              "**{}** flying a {} was killed while they were {}.{}{}\n\n"
                              "Total ISK Lost: {} ISK\n\n"
                              "__**Final Blow**__\n"
                              "**{}**\n\n".format(region_name, loser_name, ship['name'], player_task,
                                                  loser_modules, cargo_modules, '{0:,.2f}'.format(float(module_value)),
                                                  npc['name']))
        await add_loss(player)
        await player_user.send(embed=embed)
        if ship['class'] != 0:
            await self.send_global(embed, True)
        return await self.destroy_ship(player)

    async def process_roams(self):
        sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 31 OR `task` = 32 OR `task` = 33 OR `task` = 34 OR `task` = 35 '''
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
                    # Corp check
                    if roamer[23] is not None:
                        corp_info = await game_functions.get_user_corp(roamer[23])
                        corp_array = ast.literal_eval(corp_info[7])
                        if target[0] in corp_array:
                            continue
                    # Blue check
                    if roamer[21] is not None:
                        blue_array = ast.literal_eval(roamer[21])
                        if target[0] in blue_array:
                            continue
                    # Fleet check
                    if roamer[16] is not None and roamer[16] != 0:
                        sql = ''' SELECT * FROM fleet_info WHERE `fleet_id` = (?) '''
                        values = (roamer[16],)
                        fleet_info = await db.select_var(sql, values)
                        fleet_array = ast.literal_eval(fleet_info[0][3])
                        if target[0] in fleet_array:
                            continue
                    target_aggression = 4
                    if roamer[6] == 31 and (target[6] == 6 or target[6] == 10):
                        target_aggression = 20
                    elif roamer[6] == 32 and target[6] == 20:
                        target_aggression = 20
                    elif roamer[6] == 33 and target[6] == 21:
                        target_aggression = 20
                    elif roamer[6] == 34 and target[6] == 7:
                        target_aggression = 20
                    elif roamer[6] == 35 and target[6] == 11:
                        target_aggression = 20
                    conflict = await weighted_choice([(True, target_aggression), (None, 100 - target_aggression)])
                    if conflict is None:
                        break
                    elif conflict is True:
                        roamer_fleet = False
                        target_fleet = False
                        if roamer[16] is not None and roamer[16] != 0:
                            roamer_fleet = True
                        if target[16] is not None and target[16] != 0:
                            target_fleet = True
                        if target_fleet is False and roamer_fleet is False:
                            await self.solo_combat(roamer, target)
                        elif target_fleet is False and roamer_fleet is True:
                            sql = ''' SELECT * FROM fleet_info WHERE `fleet_id` = (?) '''
                            values = (roamer[16],)
                            fleet_info = await db.select_var(sql, values)
                            await self.fleet_versus_player(fleet_info[0], target, region_id)
                        elif roamer_fleet is False and target_fleet is True:
                            sql = ''' SELECT * FROM fleet_info WHERE `fleet_id` = (?) '''
                            values = (target[16],)
                            fleet_info = await db.select_var(sql, values)
                            await self.fleet_versus_player(fleet_info[0], roamer, region_id)
                        elif roamer_fleet is True and target_fleet is True:
                            sql = ''' SELECT * FROM fleet_info WHERE `fleet_id` = (?) '''
                            values = (target[16],)
                            fleet_one_info = await db.select_var(sql, values)
                            sql = ''' SELECT * FROM fleet_info WHERE `fleet_id` = (?) '''
                            values = (roamer[16],)
                            fleet_two_info = await db.select_var(sql, values)
                            await self.fleet_versus_fleet(fleet_one_info[0], fleet_two_info[0], region_id)
                        break

    async def process_ganks(self):
        sql = ''' SELECT * FROM eve_rpg_players WHERE `task` = 4 '''
        gankers = await db.select(sql)
        if gankers is None or len(gankers) is 0:
            return
        for ganker in gankers:
            region_id = int(ganker[4])
            sql = ''' SELECT * FROM eve_rpg_players WHERE `task` != 1 AND `task` != 4 AND `region` = (?) AND `player_id` != (?) '''
            values = (region_id, ganker[2])
            potential_targets = await db.select_var(sql, values)
            for target in potential_targets:
                # Blue check
                if ganker[21] is not None:
                    blue_array = ast.literal_eval(ganker[21])
                    if target[0] in blue_array:
                        return
                # Fleet check
                if ganker[16] is not None and ganker[16] != 0:
                    sql = ''' SELECT * FROM fleet_info WHERE `fleet_id` = (?) '''
                    values = (ganker[16],)
                    fleet_info = await db.select_var(sql, values)
                    fleet_array = ast.literal_eval(fleet_info[0][3])
                    if target[0] in fleet_array:
                        return
                target_aggression = 5
                if int(target[6]) == 9:
                    target_aggression = 2
                conflict = await weighted_choice([(True, target_aggression), (False, 65), (None, 45)])
                if conflict is None:
                    break
                elif conflict is True:
                    region_id = int(ganker[4])
                    region_name = await game_functions.get_region(int(region_id))
                    ganker_user, target_user = self.bot.get_user(ganker[2]), self.bot.get_user(target[2])
                    target_task = await game_functions.get_task(target[6])
                    attacker_ship, defender_ship = ast.literal_eval(ganker[14]), ast.literal_eval(target[14])
                    attacker_ship_id, defender_ship_id = attacker_ship['ship_type'], defender_ship['ship_type']
                    attacker_attack, attacker_defense, attacker_maneuver, attacker_tracking = \
                        await game_functions.get_combat_attributes(ganker, attacker_ship_id)
                    defender_attack, defender_defense, defender_maneuver, defender_tracking = \
                        await game_functions.get_combat_attributes(target, defender_ship_id)
                    attacker_ship_info = await game_functions.get_ship(int(attacker_ship['ship_type']))
                    defender_ship_info = await game_functions.get_ship(int(defender_ship['ship_type']))
                    ganker_hits, target_hits = attacker_ship_info['hit_points'], defender_ship_info['hit_points']
                    turns = 0
                    success = False
                    concord_response = random.randint(4, 12)
                    concord = True
                    for x in range(50):
                        turns += 1
                        if turns >= concord_response:
                            success = False
                            target_user.send(
                                '**PVP** - {} attempted to gank you but Concord arrived in time to prevent it.'.format(
                                    ganker_user.display_name))
                            break
                        # Figure out min/max damage
                        transversal = 1
                        if (defender_maneuver * 0.75) > attacker_tracking + 1:
                            transversal = (attacker_tracking + 1) / (defender_maneuver * 0.75)
                        minimum_attacker_damage = (attacker_attack * transversal)
                        maximum_attacker_damage = attacker_attack
                        attacker_triangular_medium = (minimum_attacker_damage + maximum_attacker_damage) / 4
                        damage = round(
                            random.triangular(minimum_attacker_damage, maximum_attacker_damage,
                                              attacker_triangular_medium), 3)
                        # Determine if ship is already damaged
                        defense = defender_defense
                        hit_points = defender_ship_info['hit_points']
                        # if defense pool exist take damage out of it
                        if defense > 0:
                            if defense >= damage:
                                defense -= damage
                            else:
                                damage -= defense
                                defense = 0
                                hit_points -= damage
                        else:
                            hit_points -= damage
                        if ganker_hits <= 0:
                            success = False
                            concord = False
                            break
                        if target_hits <= 0:
                            success = True
                            break
                    if success is True:
                        target_modules = ''
                        target_modules_array = []
                        dropped_mods = []
                        module_value = 0
                        if target[12] is not None:
                            modules = ast.literal_eval(target[12])
                            for module in modules:
                                module_item = await game_functions.get_module(module)
                                dropped = await weighted_choice([(True, 50), (False, 50)])
                                module_drop = ''
                                module_value += module_item['isk']
                                if dropped is True:
                                    dropped_mods.append(module)
                                    module_drop = ' **Module Dropped**'
                                target_modules_array.append('{} {}'.format(module_item['name'], module_drop))
                            target_module_list = '\n'.join(target_modules_array)
                            target_modules = '\n\n__Modules Lost__\n{}'.format(target_module_list)
                        isk_lost = module_value + defender_ship_info['isk']
                        embed = make_embed(icon=self.bot.user.avatar)
                        embed.set_footer(icon_url=self.bot.user.avatar_url,
                                         text="Aura - EVE Text RPG")
                        ship_image = await game_functions.get_ship_image(defender_ship['ship_type'])
                        embed.set_thumbnail(url="{}".format(ship_image))
                        embed.add_field(name="Killmail",
                                        value="**Region** - {}\n\n"
                                              "__**Loser**__\n"
                                              "**{}** flying a {} was killed while they were {}.{}\n\n"
                                              "Total ISK Lost: {} ISK\n\n"
                                              "**Killer**\n"
                                              "**{}** flying a {} while {}.\n\n".format(region_name,
                                                                                        target_user.display_name,
                                                                                        defender_ship_info['name'],
                                                                                        target_task, target_modules,
                                                                                        '{0:,.2f}'.format(
                                                                                            float(isk_lost)),
                                                                                        ganker_user.display_name,
                                                                                        attacker_ship_info['name'],
                                                                                        'Ganking'))
                        await ganker_user.send(embed=embed)
                        await target_user.send(embed=embed)
                        await self.send_global(embed, True)
                        await self.destroy_ship(target)
                        await add_loss(target)
                        await add_kill(ganker, dropped_mods)
                        await add_xp(ganker, 1)
                        await game_functions.track_player_kills(region_id)
                    target_modules = ''
                    target_modules_array = []
                    dropped_mods = []
                    module_value = 0
                    if target[12] is not None:
                        modules = ast.literal_eval(target[12])
                        for module in modules:
                            module_item = await game_functions.get_module(module)
                            dropped = await weighted_choice([(True, 50), (False, 50)])
                            module_drop = ''
                            module_value += module_item['isk']
                            if dropped is True:
                                dropped_mods.append(module)
                                module_drop = ' **Module Dropped**'
                            target_modules_array.append('{} {}'.format(module_item['name'], module_drop))
                        target_module_list = '\n'.join(target_modules_array)
                        target_modules = '\n\n__Modules Lost__\n{}'.format(target_module_list)
                    isk_lost = module_value + defender_ship_info['isk']
                    embed = make_embed(icon=self.bot.user.avatar)
                    embed.set_footer(icon_url=self.bot.user.avatar_url,
                                     text="Aura - EVE Text RPG")
                    ship_image = await game_functions.get_ship_image(attacker_ship['ship_type'])
                    embed.set_thumbnail(url="{}".format(ship_image))
                    if concord is True:
                        embed.add_field(name="Killmail",
                                        value="**Region** - {}\n\n"
                                              "__**Loser**__\n"
                                              "**{}** flying a {} was killed while they were {}.{}\n\n"
                                              "Total ISK Lost: {} ISK\n\n"
                                              "__**Final Blow**__\n"
                                              "**Concord**\n\n"
                                              "**Other Attackers**\n"
                                              "**{}** flying a {}.\n\n".format(region_name, ganker_user.display_name,
                                                                               attacker_ship_info['name'],
                                                                               'Ganking', target_modules,
                                                                               '{0:,.2f}'.format(float(isk_lost)),
                                                                               target_user.display_name,
                                                                               defender_ship_info['name'], target_task))
                    else:
                        embed.add_field(name="Killmail",
                                        value="**Region** - {}\n\n"
                                              "__**Loser**__\n"
                                              "**{}** flying a {} was killed while they were {}.{}\n\n"
                                              "Total ISK Lost: {} ISK\n\n"
                                              "__**Final Blow**__\n"
                                              "**{}** flying a {} while {}.\n\n".format(region_name,
                                                                                        ganker_user.display_name,
                                                                                        attacker_ship_info['name'],
                                                                                        'Ganking', target_modules,
                                                                                        '{0:,.2f}'.format(
                                                                                            float(isk_lost)),
                                                                                        target_user.display_name,
                                                                                        defender_ship_info['name'],
                                                                                        target_task))
                    await ganker_user.send(embed=embed)
                    await target_user.send(embed=embed)
                    await game_functions.track_player_kills(region_id)
                    await self.send_global(embed, True)
                    await self.destroy_ship(ganker)
                    await add_loss(ganker)
                    await add_kill(target, dropped_mods)
                    await add_xp(target, 1)

    async def solo_combat(self, attacker, defender):
        region = attacker[4]
        region_name = await game_functions.get_region(int(region))
        self.logger.info('Player vs. Player Battle in {}'.format(region_name))
        # Give all participants a combat timer
        attacker_fleet = [attacker]
        defender_fleet = [defender]
        await add_combat_timer(attacker)
        await add_combat_timer(defender)
        damaged_ships = {}
        combat_log = {}
        for x in range(125):
            if len(attacker_fleet) == 0 or len(defender_fleet) == 0:
                break
            merged_fleet = [y for y in
                            itertools.chain.from_iterable(itertools.zip_longest(attacker_fleet, defender_fleet)) if y]
            on_field = attacker_fleet + defender_fleet
            random.shuffle(on_field)
            # manage regen/combat log creation
            for player in merged_fleet:
                if player[2] not in combat_log:
                    combat_log[player[2]] = []
                if player[0] not in damaged_ships:
                    continue
                defense = damaged_ships[player[0]]['defense']
                player_ship = ast.literal_eval(player[14])
                player_ship_details = await game_functions.get_ship(player_ship['ship_type'])
                hit_points = player_ship_details['hit_points']
                new_defense = await game_functions.manage_regen(player, defense)
                if new_defense != defense:
                    user = self.bot.get_user(player[2])
                    name = user.display_name
                    self.logger.info(
                        '{} regened {} defense. Resulting in {} defense remaining.'.format(name, new_defense - defense,
                                                                                           new_defense))
                    combat_log[player[2]].append(
                        'Your ship has regenerated {} defense points and now has {} defense remaining and {} hit points.'.format(
                            round(new_defense - defense, 1), round(new_defense, 2), hit_points))
                damaged_ships[player[0]] = {'defense': new_defense, 'hit_points': hit_points}
            for attacker in merged_fleet:
                if len(attacker_fleet) == 0 or len(defender_fleet) == 0:
                    break
                attacker_ship = ast.literal_eval(attacker[14])
                attacker_attack, attacker_defense, attacker_maneuver, attacker_tracking = \
                    await game_functions.get_combat_attributes(attacker, attacker_ship['ship_type'])
                target = None
                target_ship_details = None
                for target in on_field:
                    # if in same fleet find new target
                    if target == attacker or ((target in attacker_fleet and attacker in attacker_fleet) or (
                            target in defender_fleet and attacker in defender_fleet)):
                        continue
                    else:
                        target_ship = ast.literal_eval(target[14])
                        target_ship_details = await game_functions.get_ship(target_ship['ship_type'])
                        target_attack, target_defense, target_maneuver, target_tracking = \
                            await game_functions.get_combat_attributes(target, attacker_ship['ship_type'])
                        break
                if target_ship_details is None:
                    continue
                # Figure out min/max damage
                transversal = 1
                if (target_maneuver * 0.75) > attacker_tracking + 1:
                    transversal = (attacker_tracking + 1) / (target_maneuver * 0.75)
                minimum_attacker_damage = (attacker_attack * transversal)
                maximum_attacker_damage = attacker_attack
                attacker_triangular_medium = (minimum_attacker_damage + maximum_attacker_damage) / 4
                damage = round(
                    random.triangular(minimum_attacker_damage, maximum_attacker_damage, attacker_triangular_medium), 3)
                original_damage = damage
                # Determine if ship is already damaged
                defense = target_defense
                hit_points = target_ship_details['hit_points']
                if target[0] in damaged_ships:
                    defense = damaged_ships[target[0]]['defense']
                    hit_points = damaged_ships[target[0]]['hit_points']
                # if defense pool exist take damage out of it
                if defense > 0:
                    if defense >= damage:
                        defense -= damage
                    else:
                        damage -= defense
                        defense = 0
                        hit_points -= damage
                else:
                    hit_points -= damage
                # if no damage done, continue
                attacker_user, target_user = self.bot.get_user(attacker[2]), self.bot.get_user(target[2])
                attacker_name, target_name = attacker_user.display_name, target_user.display_name
                self.logger.info(
                    '{} attacked {} for {} damage. Resulting in {} defense remaining and {} hits.'.format(attacker_name,
                                                                                                          target_name,
                                                                                                          original_damage,
                                                                                                          defense,
                                                                                                          hit_points))
                combat_log[attacker[2]].append(
                    '__*Attack*__ You attacked {} inflicting {} damage. Your target has {} defense remaining and {} hit points.'.format(
                        target_name, round(original_damage, 2), round(defense, 2), hit_points))
                combat_log[target[2]].append(
                    '__*Defense*__ You were attacked by {} and received {} damage. You have {} defense remaining and {} hit points.'.format(
                        attacker_name, round(original_damage, 2), round(defense, 2), hit_points))
                if hit_points > 0:
                    if target[0] in damaged_ships:
                        damaged_ships[target[0]] = {'hit_points': hit_points, 'defense': defense}
                    else:
                        damaged_ships[target[0]] = {'hit_points': hit_points, 'defense': defense}
                    # if badly damage target will attempt to flee
                    if defense < target_defense * 0.15:
                        flee = await weighted_choice([(True, target_maneuver), (False, attacker_tracking)])
                        if flee is True:
                            self.logger.info(
                                '{} has successfully fled the field.'.format(target_name))
                            combat_log[target[2]].append(
                                '__*Flee*__ You have fled the field. You have {} defense remaining and {} hit points.'.format(
                                    round(defense, 2), hit_points))
                            combat_log[attacker[2]].append(
                                '__*Enemy Fled*__ {} has disengaged and warped away.'.format(target_name))
                            if target not in attacker_fleet:
                                defender_fleet.remove(target)
                                merged_fleet.remove(target)
                                on_field.remove(target)
                                continue
                            else:
                                attacker_fleet.remove(target)
                                merged_fleet.remove(target)
                                on_field.remove(target)
                                continue
                        # Handle Cloak
                        if target[12] is not None:
                            modules = ast.literal_eval(target[12])
                            for module in modules:
                                module_item = await game_functions.get_module(module)
                                if module_item['id'] == 40 or module_item['id'] == 41:
                                    escape = await weighted_choice([(True, 50), (False, 50)])
                                    if escape is True:
                                        self.logger.info(
                                            '{} has successfully fled the field.'.format(target_name))
                                        combat_log[target[2]].append(
                                            '__*Flee*__ You have cloaked. You have {} defense remaining and {} hit points.'.format(
                                                round(defense, 2), hit_points))
                                        combat_log[attacker[2]].append(
                                            '__*Enemy Fled*__ {} has cloaked and warped away.'.format(
                                                target_name))
                                        if target not in attacker_fleet:
                                            defender_fleet.remove(target)
                                            merged_fleet.remove(target)
                                            on_field.remove(target)
                                            continue
                                        else:
                                            attacker_fleet.remove(target)
                                            merged_fleet.remove(target)
                                            on_field.remove(target)
                                            continue
                    continue
                else:
                    killing_blow = attacker
                    winner_user, loser_user = self.bot.get_user(killing_blow[2]), self.bot.get_user(target[2])
                    winner_name = winner_user.display_name
                    if killing_blow[23] is not None:
                        corp_info = await game_functions.get_user_corp(killing_blow[23])
                        winner_name = '{} [{}]'.format(winner_name, corp_info[4])
                    loser_name = self.bot.get_user(int(target[2])).display_name
                    if target[23] is not None:
                        corp_info = await game_functions.get_user_corp(target[23])
                        loser_name = '{} [{}]'.format(loser_name, corp_info[4])
                    winner_ship_obj = ast.literal_eval(killing_blow[14])
                    winner_ship = await game_functions.get_ship_name(int(winner_ship_obj['ship_type']))
                    loser_ship_obj = ast.literal_eval(target[14])
                    loser_ship = await game_functions.get_ship_name(int(loser_ship_obj['ship_type']))
                    loser_ship_info = await game_functions.get_ship(int(loser_ship_obj['ship_type']))
                    loser_modules = ''
                    cargo_modules = ''
                    loser_modules_array = []
                    cargo_modules_array = []
                    dropped_mods = []
                    module_value = 0
                    if target[12] is not None:
                        modules = ast.literal_eval(target[12])
                        for module in modules:
                            module_item = await game_functions.get_module(module)
                            dropped = await weighted_choice([(True, 50), (False, 50)])
                            module_drop = ''
                            module_value += module_item['isk']
                            if dropped is True:
                                dropped_mods.append(module)
                                module_drop = ' **Module Dropped**'
                            loser_modules_array.append('{} {}'.format(module_item['name'], module_drop))
                        loser_module_list = '\n'.join(loser_modules_array)
                        loser_modules = '\n\n__Modules Lost__\n{}'.format(loser_module_list)
                    if 'module_cargo_bay' in loser_ship_obj:
                        modules = loser_ship_obj['module_cargo_bay']
                        for module in modules:
                            module_item = await game_functions.get_module(module)
                            dropped = await weighted_choice([(True, 50), (False, 50)])
                            module_drop = ''
                            module_value += module_item['isk']
                            if dropped is True:
                                dropped_mods.append(module)
                                module_drop = ' **Module Dropped**'
                            loser_modules_array.append('{} {}'.format(module_item['name'], module_drop))
                        cargo_module_list = '\n'.join(cargo_modules_array)
                        cargo_modules = '\n\n__Cargo Lost__\n{}'.format(cargo_module_list)
                    xp_gained = await weighted_choice([(5, 45), (15, 25), (27, 15)])
                    isk_lost = module_value + loser_ship_info['isk']
                    if target not in attacker_fleet:
                        defender_fleet.remove(target)
                    else:
                        attacker_fleet.remove(target)
                    embed = make_embed(icon=self.bot.user.avatar)
                    embed.set_footer(icon_url=self.bot.user.avatar_url,
                                     text="Aura - EVE Text RPG")
                    ship_image = await game_functions.get_ship_image(loser_ship_obj['ship_type'])
                    embed.set_thumbnail(url="{}".format(ship_image))
                    embed.add_field(name="Killmail",
                                    value="**Region** - {}\n\n"
                                          "__**Loser**__\n"
                                          "**{}** flying a {} was killed.{}{}\n\n"
                                          "Total ISK Lost: {} ISK\n\n"
                                          "__**Final Blow**__\n"
                                          "**{}** flying a {}.".format(region_name, loser_name, loser_ship,
                                                                       loser_modules, cargo_modules,
                                                                       '{0:,.2f}'.format(float(isk_lost)),
                                                                       winner_name, winner_ship))
                    await winner_user.send(embed=embed)
                    await loser_user.send(embed=embed)
                    await game_functions.track_player_kills(region)
                    await self.send_global(embed, True)
                    await self.destroy_ship(target)
                    await add_loss(target)
                    await add_kill(killing_blow, dropped_mods)
                    await add_xp(killing_blow, xp_gained)
                    await self.give_pvp_loot(killing_blow)
        for key, log in combat_log.items():
            user = self.bot.get_user(key)
            entry_count = 0
            embed = make_embed(icon=self.bot.user.avatar)
            embed.set_footer(icon_url=self.bot.user.avatar_url,
                             text="Aura - EVE Text RPG")
            log_array = []
            field_count = 0
            title = 'Combat Log'
            for entry in log:
                entry_count += 1
                log_array.append(entry)
                if entry_count >= 4:
                    if field_count >= 1:
                        title = '-'
                    clean_log = '\n'.join(log_array)
                    embed.add_field(name=title,
                                    value=clean_log)
                    log_array = []
                    entry_count = 0
                    field_count += 1
                    if field_count >= 6:
                        await user.send(embed=embed)
            if field_count >= 1:
                title = '-'
            if len(log_array) > 0:
                clean_log = '\n'.join(log_array)
                embed.add_field(name=title,
                                value=clean_log)
            await user.send(embed=embed)

    async def fleet_versus_fleet(self, fleet_one, fleet_two, region, damaged=None):
        region_name = await game_functions.get_region(int(region))
        self.logger.info('Fleet vs. Fleet Battle in {}'.format(region_name))
        # Fleet stuff
        attacker_fleet_array = ast.literal_eval(fleet_one[3])
        attacker_fleet = []
        attacker_fleet_lost = []
        attacker_isk_lost = 0
        attacker_damage_dealt = 0
        attackers_in_system = 0
        for member_id in attacker_fleet_array:
            sql = ''' SELECT * FROM eve_rpg_players WHERE `id` = (?) '''
            values = (int(member_id),)
            member = await db.select_var(sql, values)
            if member[0][4] != region:
                continue
            if member[0][6] == 1 or member[0][6] == 20:
                continue
            attacker_fleet.append(member[0])
            attackers_in_system += 1
        saved_attacker_fleet = attacker_fleet
        attacker_count = len(attacker_fleet)
        defender_fleet_array = ast.literal_eval(fleet_two[3])
        defender_fleet = []
        defender_fleet_lost = []
        defender_isk_lost = 0
        defender_damage_dealt = 0
        defenders_in_system = 0
        for member_id in defender_fleet_array:
            sql = ''' SELECT * FROM eve_rpg_players WHERE `id` = (?) '''
            values = (int(member_id),)
            member = await db.select_var(sql, values)
            if member[0][4] != region:
                continue
            if member[0][6] == 1 or member[0][6] == 20:
                continue
            defender_fleet.append(member[0])
            defenders_in_system += 1
        saved_defender_fleet = defender_fleet
        defender_count = len(defender_fleet)
        if attackers_in_system == 0 or defenders_in_system == 0:
            return
        # Give all participants a combat timer
        merged_fleet = attacker_fleet + defender_fleet
        for fleet_member in merged_fleet:
            await add_combat_timer(fleet_member)
        damaged_ships = {}
        combat_log = {}
        if damaged is not None:
            damaged_ships = damaged
        flee_array = []
        fight_round = 0
        for x in range(125):
            fight_round += 1
            if len(attacker_fleet) == 0 or len(defender_fleet) == 0:
                break
            merged_fleet = [x for x in
                            itertools.chain.from_iterable(itertools.zip_longest(attacker_fleet, defender_fleet)) if x]
            on_field = attacker_fleet + defender_fleet
            random.shuffle(on_field)
            # manage regen/combat log creation
            for player in merged_fleet:
                if player[2] not in combat_log:
                    combat_log[player[2]] = []
                if player[0] not in damaged_ships:
                    continue
                defense = damaged_ships[player[0]]['defense']
                player_ship = ast.literal_eval(player[14])
                player_ship_details = await game_functions.get_ship(player_ship['ship_type'])
                hit_points = player_ship_details['hit_points']
                new_defense = await game_functions.manage_regen(player, defense)
                if new_defense != defense:
                    user = self.bot.get_user(player[2])
                    name = user.display_name
                    self.logger.info(
                        '{} regened {} defense. Resulting in {} defense remaining.'.format(name, new_defense - defense,
                                                                                           new_defense))
                    combat_log[player[2]].append(
                        'Your ship has regenerated {} defense points and now has {} defense remaining and {} hit points.'.format(
                            round(new_defense - defense, 1), round(new_defense, 2), hit_points))
                damaged_ships[player[0]] = {'defense': new_defense, 'hit_points': hit_points}
            for attacker in merged_fleet:
                if len(attacker_fleet) == 0 or len(defender_fleet) == 0:
                    break
                # add chance attack doesn't occur
                if random.random() > 0.8:
                    continue
                attacker_ship = ast.literal_eval(attacker[14])
                attacker_attack, attacker_defense, attacker_maneuver, attacker_tracking = \
                    await game_functions.get_combat_attributes(attacker, attacker_ship['ship_type'])
                target = None
                target_ship_details = None
                for target in on_field:
                    # if in same fleet find new target
                    if target == attacker or ((target in attacker_fleet and attacker in attacker_fleet) or (
                            target in defender_fleet and attacker in defender_fleet)):
                        continue
                    else:
                        target_ship = ast.literal_eval(target[14])
                        target_ship_details = await game_functions.get_ship(target_ship['ship_type'])
                        target_attack, target_defense, target_maneuver, target_tracking = \
                            await game_functions.get_combat_attributes(target, attacker_ship['ship_type'])
                        break
                if target_ship_details is None:
                    continue
                # Figure out min/max damage
                transversal = 1
                if (target_maneuver * 0.75) > attacker_tracking + 1:
                    transversal = (attacker_tracking + 1) / (target_maneuver * 0.75)
                minimum_attacker_damage = (attacker_attack * transversal)
                maximum_attacker_damage = attacker_attack
                attacker_triangular_medium = (minimum_attacker_damage + maximum_attacker_damage) / 4
                damage = round(
                    random.triangular(minimum_attacker_damage, maximum_attacker_damage, attacker_triangular_medium), 3)
                original_damage = damage
                # log damage done for BR
                if attacker in attacker_fleet:
                    attacker_damage_dealt += damage
                else:
                    defender_damage_dealt += damage
                # Determine if ship is already damaged
                defense = target_defense
                hit_points = target_ship_details['hit_points']
                if target[0] in damaged_ships:
                    defense = damaged_ships[target[0]]['defense']
                    hit_points = damaged_ships[target[0]]['hit_points']
                # if defense pool exist take damage out of it
                if defense > 0:
                    if defense >= damage:
                        defense -= damage
                    else:
                        damage -= defense
                        defense = 0
                        hit_points -= damage
                else:
                    hit_points -= damage
                # if no damage done, continue
                attacker_user, target_user = self.bot.get_user(attacker[2]), self.bot.get_user(target[2])
                attacker_name, target_name = attacker_user.display_name, target_user.display_name
                self.logger.info(
                    '{} attacked {} for {} damage. Resulting in {} defense remaining and {} hits.'.format(attacker_name,
                                                                                                          target_name,
                                                                                                          original_damage,
                                                                                                          defense,
                                                                                                          hit_points))
                combat_log[attacker[2]].append(
                    '__*Attack*__ You attacked {} inflicting {} damage. Your target has {} defense remaining and {} hit points.'.format(
                        target_name, round(original_damage, 2), round(defense, 2), hit_points))
                combat_log[target[2]].append(
                    '__*Defense*__ You were attacked by {} and received {} damage. You have {} defense remaining and {} hit points.'.format(
                        attacker_name, round(original_damage, 2), round(defense, 2), hit_points))
                # if no damage done, continue
                if damage <= 0:
                    continue
                # if target survives, store damage
                if hit_points > 0:
                    if target[0] in damaged_ships:
                        attackers = list(set(damaged_ships[target[0]]['attackers'].append(attacker[0])))
                        damaged_ships[target[0]] = {'hit_points': hit_points, 'defense': defense,
                                                    'attackers': attackers}
                    else:
                        damaged_ships[target[0]] = {'hit_points': hit_points, 'defense': defense,
                                                    'attackers': [attacker[0]]}
                    # if badly damage target will attempt to flee
                    if defense < target_defense * 0.15:
                        flee = await weighted_choice([(True, target_maneuver), (False, attacker_tracking)])
                        if flee is True:
                            self.logger.info(
                                '{} has successfully fled the field.'.format(target_name))
                            combat_log[target[2]].append(
                                '__*Flee*__ You have fled the field. You have {} defense remaining and {} hit points.'.format(
                                    round(defense, 2), hit_points))
                            combat_log[attacker[2]].append(
                                '__*Enemy Fled*__ {} has disengaged and warped away.'.format(target_name))
                            if target not in attacker_fleet:
                                defender_fleet.remove(target)
                                merged_fleet.remove(target)
                                on_field.remove(target)
                                continue
                            else:
                                attacker_fleet.remove(target)
                                merged_fleet.remove(target)
                                on_field.remove(target)
                                continue
                        # Handle Cloak
                        if target[12] is not None:
                            modules = ast.literal_eval(target[12])
                            for module in modules:
                                module_item = await game_functions.get_module(module)
                                if module_item['id'] == 40 or module_item['id'] == 41:
                                    escape = await weighted_choice([(True, 50), (False, 50)])
                                    if escape is True:
                                        self.logger.info(
                                            '{} has successfully fled the field.'.format(target_name))
                                        combat_log[target[2]].append(
                                            '__*Flee*__ You have cloaked. You have {} defense remaining and {} hit points.'.format(
                                                round(defense, 2), hit_points))
                                        combat_log[attacker[2]].append(
                                            '__*Enemy Fled*__ {} has cloaked and warped away.'.format(
                                                target_name))
                                        flee_array.append(target[0])
                                        if target not in attacker_fleet:
                                            defender_fleet.remove(target)
                                            merged_fleet.remove(target)
                                            on_field.remove(target)
                                            continue
                                        else:
                                            attacker_fleet.remove(target)
                                            merged_fleet.remove(target)
                                            on_field.remove(target)
                                            continue
                else:
                    if target in merged_fleet:
                        merged_fleet.remove(target)
                    if target in on_field:
                        on_field.remove(target)
                    killing_blow = attacker
                    other_names = []
                    other_users = []
                    if target[0] in damaged_ships:
                        for on_mail in damaged_ships[target[0]]['attackers']:
                            if on_mail == killing_blow[0]:
                                continue
                            sql = ''' SELECT * FROM eve_rpg_players WHERE `id` = (?) '''
                            values = (on_mail,)
                            player = await db.select_var(sql, values)
                            on_mail_name = self.bot.get_user(int(player[0][2])).display_name
                            if player[0][23] is not None:
                                corp_info = await game_functions.get_user_corp(player[0][23])
                                on_mail_name = '{} [{}]'.format(on_mail_name, corp_info[4])
                            other_users.append(player[0])
                            other_names.append('{}'.format(on_mail_name))
                    clean_names = '\n'.join(other_names)
                    if len(other_names) > 6:
                        clean_names = '\n{} fleet members.'.format(len(other_names))
                    winner_user, loser_user = self.bot.get_user(killing_blow[2]), self.bot.get_user(target[2])
                    winner_name = winner_user.display_name
                    if killing_blow[23] is not None:
                        corp_info = await game_functions.get_user_corp(killing_blow[23])
                        winner_name = '{} [{}]'.format(winner_name, corp_info[4])
                    loser_name = self.bot.get_user(int(target[2])).display_name
                    if target[23] is not None:
                        corp_info = await game_functions.get_user_corp(target[23])
                        loser_name = '{} [{}]'.format(loser_name, corp_info[4])
                    winner_ship_obj = ast.literal_eval(killing_blow[14])
                    winner_ship = await game_functions.get_ship_name(int(winner_ship_obj['ship_type']))
                    loser_ship_obj = ast.literal_eval(target[14])
                    loser_ship = await game_functions.get_ship_name(int(loser_ship_obj['ship_type']))
                    loser_ship_info = await game_functions.get_ship(int(loser_ship_obj['ship_type']))
                    loser_modules = ''
                    cargo_modules = ''
                    loser_modules_array = []
                    cargo_modules_array = []
                    dropped_mods = []
                    module_value = 0
                    if target[12] is not None:
                        modules = ast.literal_eval(target[12])
                        for module in modules:
                            module_item = await game_functions.get_module(module)
                            dropped = await weighted_choice([(True, 50), (False, 50)])
                            module_drop = ''
                            module_value += module_item['isk']
                            if dropped is True:
                                dropped_mods.append(module)
                                module_drop = ' **Module Dropped**'
                            loser_modules_array.append('{} {}'.format(module_item['name'], module_drop))
                        loser_module_list = '\n'.join(loser_modules_array)
                        loser_modules = '\n\n__Modules Lost__\n{}'.format(loser_module_list)
                    if 'module_cargo_bay' in loser_ship_obj:
                        modules = loser_ship_obj['module_cargo_bay']
                        for module in modules:
                            module_item = await game_functions.get_module(module)
                            dropped = await weighted_choice([(True, 50), (False, 50)])
                            module_drop = ''
                            module_value += module_item['isk']
                            if dropped is True:
                                dropped_mods.append(module)
                                module_drop = ' **Module Dropped**'
                            loser_modules_array.append('{} {}'.format(module_item['name'], module_drop))
                        cargo_module_list = '\n'.join(cargo_modules_array)
                        cargo_modules = '\n\n__Cargo Lost__\n{}'.format(cargo_module_list)
                    xp_gained = await weighted_choice([(5, 45), (15, 25), (27, 15)])
                    isk_lost = module_value + loser_ship_info['isk']
                    if target in attacker_fleet:
                        attacker_fleet.remove(target)
                        attacker_fleet_lost.append(target)
                        attacker_isk_lost += isk_lost
                    elif target in defender_fleet:
                        defender_fleet.remove(target)
                        defender_fleet_lost.append(target)
                        defender_isk_lost += isk_lost
                    embed = make_embed(icon=self.bot.user.avatar)
                    embed.set_footer(icon_url=self.bot.user.avatar_url,
                                     text="Aura - EVE Text RPG")
                    ship_image = await game_functions.get_ship_image(loser_ship_obj['ship_type'])
                    embed.set_thumbnail(url="{}".format(ship_image))
                    embed.add_field(name="Killmail",
                                    value="**Region** - {}\n\n"
                                          "__**Loser**__\n"
                                          "**{}** flying a {} was killed.{}{}\n\n"
                                          "Total ISK Lost: {} ISK\n\n"
                                          "__**Final Blow**__\n"
                                          "**{}** flying a {}.\n\n"
                                          "__**Other Killers**__\n{}".format(region_name, loser_name, loser_ship,
                                                                             loser_modules, cargo_modules,
                                                                             '{0:,.2f}'.format(float(isk_lost)),
                                                                             winner_name, winner_ship, clean_names))
                    await winner_user.send(embed=embed)
                    await loser_user.send(embed=embed)
                    await game_functions.track_player_kills(region)
                    await self.send_global(embed, True)
                    await self.destroy_ship(target)
                    await add_loss(target)
                    await add_kill(killing_blow, dropped_mods)
                    await add_xp(killing_blow, xp_gained)
                    await self.give_pvp_loot(killing_blow)
                    dropped_mods = []
                    for user in other_users:
                        await add_kill(user, dropped_mods)
                        await add_xp(user, xp_gained)
            if len(merged_fleet) == 0:
                break
        ongoing_text = ''
        self.logger.info(
            'Fight lasted {} rounds. Fleet 1 lost {} ships and took {} damage. Fleet 2 lost {} ships and took {} damage'.format(
                fight_round, len(attacker_fleet_lost), defender_damage_dealt, len(defender_fleet_lost),
                attacker_damage_dealt))
        if len(attacker_fleet) > 0 and len(defender_fleet) > 0:
            ongoing_text = '\n\n**This Battle Is Still Ongoing**'
            self.ongoing_fleet_fights[region] = {'attacker': attacker_fleet, 'defender': defender_fleet,
                                                 'region': region, 'damaged': damaged_ships}
        if len(attacker_fleet_lost) > 0 or len(defender_fleet_lost) > 0:
            embed = make_embed(icon=self.bot.user.avatar)
            embed.set_footer(icon_url=self.bot.user.avatar_url,
                             text="Aura - EVE Text RPG")
            embed.add_field(name="Fleet Battle Report",
                            value="Region: {}\n"
                                  "Total Players Involved: {}\n"
                                  "Ships Destroyed: {}\n"
                                  "Total ISK Lost: {} ISK\n"
                                  "Total Damage Done: {}\n{}".format(region_name, defender_count + attacker_count,
                                                                     len(attacker_fleet_lost) + len(
                                                                         defender_fleet_lost),
                                                                     '{0:,.2f}'.format(
                                                                         float(attacker_isk_lost + defender_isk_lost)),
                                                                     attacker_damage_dealt + defender_damage_dealt,
                                                                     ongoing_text),
                            inline=False)
            embed.add_field(name="Fleet One Stats",
                            value="Fleet Size: {} Players\n"
                                  "Total Losses: {}\n"
                                  "ISK Lost: {} ISK\n"
                                  "Total Damage Received: {}".format(attacker_count, len(attacker_fleet_lost),
                                                                     '{0:,.2f}'.format(float(attacker_isk_lost)),
                                                                     defender_damage_dealt),
                            inline=False)
            fleet_one_members_array = []
            counter = 0
            for member in saved_attacker_fleet:
                member_ship = ast.literal_eval(member[14])
                ship_details = await game_functions.get_ship(member_ship['ship_type'])
                name = self.bot.get_user(int(member[2])).display_name
                if member in attacker_fleet_lost:
                    fleet_one_members_array.append('**Killed** {} - *{}*'.format(name, ship_details['name']))
                elif member[0] in flee_array:
                    fleet_one_members_array.append('**Fled Battle** {} - *{}*'.format(name, ship_details['name']))
                else:
                    fleet_one_members_array.append('{} - *{}*'.format(name, ship_details['name']))
                if counter >= 10:
                    counter = 0
                    fleet_one_members_clean = '\n'.join(fleet_one_members_array)
                    embed.add_field(name="__Fleet One Members__",
                                    value=fleet_one_members_clean)
                    fleet_one_members_array = []
            if len(fleet_one_members_array) > 0:
                fleet_one_members_clean = '\n'.join(fleet_one_members_array)
                embed.add_field(name="__Fleet One Members__",
                                value=fleet_one_members_clean)
            embed.add_field(name="Fleet Two Stats",
                            value="Fleet Size: {} Players\n"
                                  "Total Losses: {}\n"
                                  "ISK Lost: {} ISK\n"
                                  "Total Damage Received: {}".format(defender_count, len(defender_fleet_lost),
                                                                     '{0:,.2f}'.format(float(defender_isk_lost)),
                                                                     attacker_damage_dealt),
                            inline=False)
            fleet_two_members_array = []
            counter = 0
            for member in saved_defender_fleet:
                member_ship = ast.literal_eval(member[14])
                ship_details = await game_functions.get_ship(member_ship['ship_type'])
                name = self.bot.get_user(int(member[2])).display_name
                if member in defender_fleet_lost:
                    fleet_two_members_array.append('**Killed** {} - *{}*'.format(name, ship_details['name']))
                elif member[0] in flee_array:
                    fleet_one_members_array.append('**Fled Battle** {} - *{}*'.format(name, ship_details['name']))
                else:
                    fleet_two_members_array.append('{} - *{}*'.format(name, ship_details['name']))
                if counter >= 10:
                    counter = 0
                    fleet_two_members_clean = '\n'.join(fleet_two_members_array)
                    embed.add_field(name="__Fleet Two Members__",
                                    value=fleet_two_members_clean)
                    fleet_two_members_array = []
            if len(fleet_two_members_array) > 0:
                fleet_two_members_clean = '\n'.join(fleet_two_members_array)
                embed.add_field(name="__Fleet Two Members__",
                                value=fleet_two_members_clean)
            for fleet_member in merged_fleet:
                user = self.bot.get_user(fleet_member[2])
                await user.send(embed=embed)
            await self.send_global(embed, True)
        for key, log in combat_log.items():
            user = self.bot.get_user(key)
            entry_count = 0
            embed = make_embed(icon=self.bot.user.avatar)
            embed.set_footer(icon_url=self.bot.user.avatar_url,
                             text="Aura - EVE Text RPG")
            log_array = []
            field_count = 0
            title = 'Combat Log'
            for entry in log:
                entry_count += 1
                log_array.append(entry)
                if entry_count >= 4:
                    if field_count >= 1:
                        title = '-'
                    clean_log = '\n'.join(log_array)
                    embed.add_field(name=title,
                                    value=clean_log)
                    log_array = []
                    entry_count = 0
                    field_count += 1
                    if field_count >= 6:
                        await user.send(embed=embed)
            if field_count >= 1:
                title = '-'
            if len(log_array) > 0:
                clean_log = '\n'.join(log_array)
                embed.add_field(name=title,
                                value=clean_log)
            await user.send(embed=embed)

    async def fleet_versus_player(self, fleet_one, player, region):
        region_name = await game_functions.get_region(int(region))
        self.logger.info('Fleet vs. Player Battle in {}'.format(region_name))
        # Fleet stuff
        attacker_fleet_array = ast.literal_eval(fleet_one[3])
        attacker_fleet = []
        saved_attacker_fleet = []
        attacker_fleet_lost = []
        attacker_isk_lost = 0
        attacker_damage_dealt = 0
        attackers_in_system = 0
        for member_id in attacker_fleet_array:
            sql = ''' SELECT * FROM eve_rpg_players WHERE `id` = (?) '''
            values = (int(member_id),)
            member = await db.select_var(sql, values)
            if member[0][4] != region:
                continue
            if member[0][6] == 1 or member[0][6] == 20:
                continue
            saved_attacker_fleet.append(member[0])
            attacker_fleet.append(member[0])
            attackers_in_system += 1
        if attackers_in_system == 0:
            return
        attacker_count = len(attacker_fleet)
        defender_fleet = [player]
        saved_defender_fleet = [player]
        defender_count = len(defender_fleet)
        defender_fleet_lost = []
        defender_isk_lost = 0
        defender_damage_dealt = 0
        # Give all participants a combat timer
        merged_fleet = attacker_fleet + defender_fleet
        for fleet_member in merged_fleet:
            await add_combat_timer(fleet_member)
        damaged_ships = {}
        combat_log = {}
        flee_array = []
        fight_round = 0
        for x in range(125):
            fight_round += 1
            if len(attacker_fleet) == 0 or len(defender_fleet) == 0:
                break
            merged_fleet = [x for x in
                            itertools.chain.from_iterable(itertools.zip_longest(attacker_fleet, defender_fleet)) if x]
            on_field = attacker_fleet + defender_fleet
            random.shuffle(on_field)
            # manage regen/combat log creation
            for player in merged_fleet:
                if player[2] not in combat_log:
                    combat_log[player[2]] = []
                if player[0] not in damaged_ships:
                    continue
                defense = damaged_ships[player[0]]['defense']
                player_ship = ast.literal_eval(player[14])
                player_ship_details = await game_functions.get_ship(player_ship['ship_type'])
                hit_points = player_ship_details['hit_points']
                new_defense = await game_functions.manage_regen(player, defense)
                if new_defense != defense:
                    user = self.bot.get_user(player[2])
                    name = user.display_name
                    self.logger.info(
                        '{} regened {} defense. Resulting in {} defense remaining.'.format(name, new_defense - defense,
                                                                                           new_defense))
                    combat_log[player[2]].append(
                        'Your ship has regenerated {} defense points and now has {} defense remaining and {} hit points.'.format(
                            round(new_defense - defense, 1), round(new_defense, 2), hit_points))
                damaged_ships[player[0]] = {'defense': new_defense, 'hit_points': hit_points}
            for attacker in merged_fleet:
                if len(attacker_fleet) == 0 or len(defender_fleet) == 0:
                    break
                # add chance attack doesn't occur
                if random.random() > 0.8:
                    continue
                attacker_ship = ast.literal_eval(attacker[14])
                attacker_attack, attacker_defense, attacker_maneuver, attacker_tracking = \
                    await game_functions.get_combat_attributes(attacker, attacker_ship['ship_type'])
                target = None
                target_ship_details = None
                for target in on_field:
                    # if in same fleet find new target
                    if target == attacker or ((target in attacker_fleet and attacker in attacker_fleet) or (
                            target in defender_fleet and attacker in defender_fleet)):
                        continue
                    else:
                        target_ship = ast.literal_eval(target[14])
                        target_ship_details = await game_functions.get_ship(target_ship['ship_type'])
                        target_attack, target_defense, target_maneuver, target_tracking = \
                            await game_functions.get_combat_attributes(target, attacker_ship['ship_type'])
                        break
                if target_ship_details is None:
                    continue
                # Figure out min/max damage
                transversal = 1
                if (target_maneuver * 0.75) > attacker_tracking + 1:
                    transversal = (attacker_tracking + 1) / (target_maneuver * 0.75)
                minimum_attacker_damage = (attacker_attack * transversal)
                maximum_attacker_damage = attacker_attack
                attacker_triangular_medium = (minimum_attacker_damage + maximum_attacker_damage) / 4
                damage = round(
                    random.triangular(minimum_attacker_damage, maximum_attacker_damage, attacker_triangular_medium), 3)
                original_damage = damage
                # log damage done for BR
                if attacker in attacker_fleet:
                    attacker_damage_dealt += damage
                else:
                    defender_damage_dealt += damage
                # Determine if ship is already damaged
                defense = target_defense
                hit_points = target_ship_details['hit_points']
                if target[0] in damaged_ships:
                    defense = damaged_ships[target[0]]['defense']
                    hit_points = damaged_ships[target[0]]['hit_points']
                # if defense pool exist take damage out of it
                if defense > 0:
                    if defense >= damage:
                        defense -= damage
                    else:
                        damage -= defense
                        defense = 0
                        hit_points -= damage
                else:
                    hit_points -= damage
                # if no damage done, continue
                attacker_user, target_user = self.bot.get_user(attacker[2]), self.bot.get_user(target[2])
                attacker_name, target_name = attacker_user.display_name, target_user.display_name
                self.logger.info(
                    '{} attacked {} for {} damage. Resulting in {} defense remaining and {} hits.'.format(attacker_name,
                                                                                                          target_name,
                                                                                                          original_damage,
                                                                                                          defense,
                                                                                                          hit_points))
                combat_log[attacker[2]].append(
                    '__*Attack*__ You attacked {} inflicting {} damage. Your target has {} defense remaining and {} hit points.'.format(
                        target_name, round(original_damage, 2), round(defense, 2), hit_points))
                combat_log[target[2]].append(
                    '__*Defense*__ You were attacked by {} and received {} damage. You have {} defense remaining and {} hit points.'.format(
                        attacker_name, round(original_damage, 2), round(defense, 2), hit_points))
                if damage <= 0:
                    continue
                # if target survives, store damage
                if hit_points > 0:
                    if target[0] in damaged_ships:
                        attackers = list(set(damaged_ships[target[0]]['attackers'].append(attacker[0])))
                        damaged_ships[target[0]] = {'hit_points': hit_points, 'defense': defense,
                                                    'attackers': attackers}
                    else:
                        damaged_ships[target[0]] = {'hit_points': hit_points, 'defense': defense,
                                                    'attackers': [attacker[0]]}
                    # if badly damage target will attempt to flee
                    if defense < target_defense * 0.15:
                        flee = await weighted_choice([(True, target_maneuver), (False, attacker_tracking)])
                        if flee is True:
                            self.logger.info(
                                '{} has successfully fled the field.'.format(target_name))
                            combat_log[target[2]].append(
                                '__*Flee*__ You have fled the field. You have {} defense remaining and {} hit points.'.format(
                                    round(defense, 2), hit_points))
                            combat_log[attacker[2]].append(
                                '__*Enemy Fled*__ {} has disengaged and warped away.'.format(target_name))
                            if target not in attacker_fleet:
                                defender_fleet.remove(target)
                                merged_fleet.remove(target)
                                on_field.remove(target)
                                continue
                            else:
                                attacker_fleet.remove(target)
                                merged_fleet.remove(target)
                                on_field.remove(target)
                                continue
                        # Handle Cloak
                        if target[12] is not None:
                            modules = ast.literal_eval(target[12])
                            for module in modules:
                                module_item = await game_functions.get_module(module)
                                if module_item['id'] == 40 or module_item['id'] == 41:
                                    escape = await weighted_choice([(True, 50), (False, 50)])
                                    if escape is True:
                                        self.logger.info(
                                            '{} has successfully fled the field.'.format(target_name))
                                        combat_log[target[2]].append(
                                            '__*Flee*__ You have cloaked. You have {} defense remaining and {} hit points.'.format(
                                                round(defense, 2), hit_points))
                                        combat_log[attacker[2]].append(
                                            '__*Enemy Fled*__ {} has cloaked and warped away.'.format(
                                                target_name))
                                        flee_array.append(target[0])
                                        if target not in attacker_fleet:
                                            defender_fleet.remove(target)
                                            merged_fleet.remove(target)
                                            on_field.remove(target)
                                            continue
                                        else:
                                            attacker_fleet.remove(target)
                                            merged_fleet.remove(target)
                                            on_field.remove(target)
                                            continue
                else:
                    if target in merged_fleet:
                        merged_fleet.remove(target)
                    if target in on_field:
                        on_field.remove(target)
                    killing_blow = attacker
                    other_names = []
                    other_users = []
                    if target[0] in damaged_ships:
                        for on_mail in damaged_ships[target[0]]['attackers']:
                            if on_mail == killing_blow[0]:
                                continue
                            sql = ''' SELECT * FROM eve_rpg_players WHERE `id` = (?) '''
                            values = (on_mail,)
                            player = await db.select_var(sql, values)
                            on_mail_name = self.bot.get_user(int(player[0][2])).display_name
                            if player[0][23] is not None:
                                corp_info = await game_functions.get_user_corp(player[0][23])
                                on_mail_name = '{} [{}]'.format(on_mail_name, corp_info[4])
                            other_users.append(player[0])
                            other_names.append('{}'.format(on_mail_name))
                    clean_names = '\n'.join(other_names)
                    if len(other_names) > 6:
                        clean_names = '\n{} fleet members.'.format(len(other_names))
                    winner_user, loser_user = self.bot.get_user(killing_blow[2]), self.bot.get_user(target[2])
                    winner_name = winner_user.display_name
                    if killing_blow[23] is not None:
                        corp_info = await game_functions.get_user_corp(killing_blow[23])
                        winner_name = '{} [{}]'.format(winner_name, corp_info[4])
                    loser_name = self.bot.get_user(int(target[2])).display_name
                    if target[23] is not None:
                        corp_info = await game_functions.get_user_corp(target[23])
                        loser_name = '{} [{}]'.format(loser_name, corp_info[4])
                    winner_ship_obj = ast.literal_eval(killing_blow[14])
                    winner_ship = await game_functions.get_ship_name(int(winner_ship_obj['ship_type']))
                    loser_ship_obj = ast.literal_eval(target[14])
                    loser_ship = await game_functions.get_ship_name(int(loser_ship_obj['ship_type']))
                    loser_ship_info = await game_functions.get_ship(int(loser_ship_obj['ship_type']))
                    loser_modules = ''
                    cargo_modules = ''
                    loser_modules_array = []
                    cargo_modules_array = []
                    dropped_mods = []
                    module_value = 0
                    if target[12] is not None:
                        modules = ast.literal_eval(target[12])
                        for module in modules:
                            module_item = await game_functions.get_module(module)
                            dropped = await weighted_choice([(True, 50), (False, 50)])
                            module_drop = ''
                            module_value += module_item['isk']
                            if dropped is True:
                                dropped_mods.append(module)
                                module_drop = ' **Module Dropped**'
                            loser_modules_array.append('{} {}'.format(module_item['name'], module_drop))
                        loser_module_list = '\n'.join(loser_modules_array)
                        loser_modules = '\n\n__Modules Lost__\n{}'.format(loser_module_list)
                    if 'module_cargo_bay' in loser_ship_obj:
                        modules = loser_ship_obj['module_cargo_bay']
                        for module in modules:
                            module_item = await game_functions.get_module(module)
                            dropped = await weighted_choice([(True, 50), (False, 50)])
                            module_drop = ''
                            module_value += module_item['isk']
                            if dropped is True:
                                dropped_mods.append(module)
                                module_drop = ' **Module Dropped**'
                            loser_modules_array.append('{} {}'.format(module_item['name'], module_drop))
                        cargo_module_list = '\n'.join(cargo_modules_array)
                        cargo_modules = '\n\n__Cargo Lost__\n{}'.format(cargo_module_list)
                    xp_gained = await weighted_choice([(5, 45), (15, 25), (27, 15)])
                    isk_lost = module_value + loser_ship_info['isk']
                    if target in attacker_fleet:
                        attacker_fleet.remove(target)
                        attacker_fleet_lost.append(target)
                        attacker_isk_lost += isk_lost
                    elif target in defender_fleet:
                        defender_fleet.remove(target)
                        defender_fleet_lost.append(target)
                        defender_isk_lost += isk_lost
                    embed = make_embed(icon=self.bot.user.avatar)
                    embed.set_footer(icon_url=self.bot.user.avatar_url,
                                     text="Aura - EVE Text RPG")
                    ship_image = await game_functions.get_ship_image(loser_ship_obj['ship_type'])
                    embed.set_thumbnail(url="{}".format(ship_image))
                    embed.add_field(name="Killmail",
                                    value="**Region** - {}\n\n"
                                          "__**Loser**__\n"
                                          "**{}** flying a {} was killed.{}{}\n\n"
                                          "Total ISK Lost: {} ISK\n\n"
                                          "__**Final Blow**__\n"
                                          "**{}** flying a {}.\n\n"
                                          "__**Other Killers**__\n{}".format(region_name, loser_name, loser_ship,
                                                                             loser_modules, cargo_modules,
                                                                             '{0:,.2f}'.format(float(isk_lost)),
                                                                             winner_name, winner_ship, clean_names))
                    await winner_user.send(embed=embed)
                    await loser_user.send(embed=embed)
                    await game_functions.track_player_kills(region)
                    await self.send_global(embed, True)
                    await self.destroy_ship(target)
                    await add_loss(target)
                    await add_kill(killing_blow, dropped_mods)
                    await add_xp(killing_blow, xp_gained)
                    await self.give_pvp_loot(killing_blow)
                    dropped_mods = []
                    for user in other_users:
                        await add_kill(user, dropped_mods)
                        await add_xp(user, xp_gained)
            if len(merged_fleet) == 0:
                break
        self.logger.info(
            'Fight lasted {} rounds. Fleet lost {} ships and took {} damage. Player lost {} ships and took {} damage'.format(
                fight_round, len(attacker_fleet_lost), defender_damage_dealt, len(defender_fleet_lost),
                attacker_damage_dealt))
        ongoing_text = ''
        if len(attacker_fleet) > 0 and len(defender_fleet) > 0:
            ongoing_text = '\n\n**This Battle Is Still Ongoing**'
            self.ongoing_fleet_fights[region] = {'attacker': attacker_fleet, 'defender': defender_fleet,
                                                 'region': region, 'damaged': damaged_ships}
        if len(attacker_fleet_lost) > 0 or len(defender_fleet_lost) > 0:
            embed = make_embed(icon=self.bot.user.avatar)
            embed.set_footer(icon_url=self.bot.user.avatar_url,
                             text="Aura - EVE Text RPG")
            embed.add_field(name="Fleet Battle Report",
                            value="Region: {}\n"
                                  "Total Players Involved: {}\n"
                                  "Ships Destroyed: {}\n"
                                  "Total ISK Lost: {} ISK\n"
                                  "Total Damage Done: {}\n{}".format(region_name, defender_count + attacker_count,
                                                                     len(attacker_fleet_lost) + len(
                                                                         defender_fleet_lost),
                                                                     '{0:,.2f}'.format(
                                                                         float(attacker_isk_lost + defender_isk_lost)),
                                                                     attacker_damage_dealt + defender_damage_dealt,
                                                                     ongoing_text),
                            inline=False)
            embed.add_field(name="Fleet One Stats",
                            value="Fleet Size: {} Players\n"
                                  "Total Losses: {}\n"
                                  "ISK Lost: {} ISK\n"
                                  "Total Damage Received: {}".format(attacker_count, len(attacker_fleet_lost),
                                                                     '{0:,.2f}'.format(float(attacker_isk_lost)),
                                                                     defender_damage_dealt),
                            inline=False)
            fleet_one_members_array = []
            counter = 0
            for member in saved_attacker_fleet:
                member_ship = ast.literal_eval(member[14])
                ship_details = await game_functions.get_ship(member_ship['ship_type'])
                name = self.bot.get_user(int(member[2])).display_name
                if member in attacker_fleet_lost:
                    fleet_one_members_array.append('**Killed** {} - *{}*'.format(name, ship_details['name']))
                elif member[0] in flee_array:
                    fleet_one_members_array.append('**Fled Battle** {} - *{}*'.format(name, ship_details['name']))
                else:
                    fleet_one_members_array.append('{} - *{}*'.format(name, ship_details['name']))
                if counter >= 10:
                    counter = 0
                    fleet_one_members_clean = '\n'.join(fleet_one_members_array)
                    embed.add_field(name="__Fleet One Members__",
                                    value=fleet_one_members_clean)
                    fleet_one_members_array = []
            if len(fleet_one_members_array) > 0:
                fleet_one_members_clean = '\n'.join(fleet_one_members_array)
                embed.add_field(name="__Fleet One Members__",
                                value=fleet_one_members_clean)
            embed.add_field(name="Fleet Two Stats",
                            value="Fleet Size: {} Players\n"
                                  "Total Losses: {}\n"
                                  "ISK Lost: {} ISK\n"
                                  "Total Damage Received: {}".format(defender_count, len(defender_fleet_lost),
                                                                     '{0:,.2f}'.format(float(defender_isk_lost)),
                                                                     attacker_damage_dealt),
                            inline=False)
            fleet_two_members_array = []
            counter = 0
            for member in saved_defender_fleet:
                member_ship = ast.literal_eval(member[14])
                ship_details = await game_functions.get_ship(member_ship['ship_type'])
                name = self.bot.get_user(int(member[2])).display_name
                if member in defender_fleet_lost:
                    fleet_two_members_array.append('**Killed** {} - *{}*'.format(name, ship_details['name']))
                elif member[0] in flee_array:
                    fleet_two_members_array.append('**Fled Battle** {} - *{}*'.format(name, ship_details['name']))
                else:
                    fleet_two_members_array.append('{} - *{}*'.format(name, ship_details['name']))
                if counter >= 10:
                    counter = 0
                    fleet_two_members_clean = '\n'.join(fleet_two_members_array)
                    embed.add_field(name="__Fleet Two Members__",
                                    value=fleet_two_members_clean)
                    fleet_two_members_array = []
            if len(fleet_two_members_array) > 0:
                fleet_two_members_clean = '\n'.join(fleet_two_members_array)
                embed.add_field(name="__Fleet Two Members__",
                                value=fleet_two_members_clean)
            for fleet_member in merged_fleet:
                user = self.bot.get_user(fleet_member[2])
                await user.send(embed=embed)
            await self.send_global(embed, True)
        for key, log in combat_log.items():
            user = self.bot.get_user(key)
            entry_count = 0
            embed = make_embed(icon=self.bot.user.avatar)
            embed.set_footer(icon_url=self.bot.user.avatar_url,
                             text="Aura - EVE Text RPG")
            log_array = []
            field_count = 0
            title = 'Combat Log'
            for entry in log:
                entry_count += 1
                log_array.append(entry)
                if entry_count >= 4:
                    if field_count >= 1:
                        title = '-'
                    clean_log = '\n'.join(log_array)
                    embed.add_field(name=title,
                                    value=clean_log)
                    log_array = []
                    entry_count = 0
                    field_count += 1
                    if field_count >= 6:
                        await user.send(embed=embed)
            if field_count >= 1:
                title = '-'
            if len(log_array) > 0:
                clean_log = '\n'.join(log_array)
                embed.add_field(name=title,
                                value=clean_log)
            await user.send(embed=embed)

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

    async def destroy_ship(self, player):
        player = await game_functions.refresh_player(player)
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
            await update_journal(player, lost_ship['insurance_payout'], 'Received Insurance')
            return await db.execute_sql(sql, values)

    async def give_pvp_loot(self, player):
        player = await game_functions.refresh_player(player)
        ship = ast.literal_eval(player[14])
        tier_1_amount = random.randint(1, 50)
        tier_1 = await weighted_choice([(True, 90), (False, 10)])
        tier_1_text = ''
        tier_2_amount = random.randint(1, 10)
        tier_2 = await weighted_choice([(True, 55), (False, 45)])
        tier_2_text = ''
        tier_3_amount = random.randint(1, 3)
        tier_3 = await weighted_choice([(True, 5), (False, 95)])
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
            loot_type = await weighted_choice([(2, 35), (3, 65)])
            component = await game_functions.get_component(loot_type)
            tier_2_loot = {'type_id': loot_type, 'id': loot_id, 'amount': tier_2_amount}
            loot.append(tier_2_loot)
            tier_2_text = '{}x {}\n'.format(tier_2_amount, component['name'])
        if tier_3 is True:
            loot_id = await game_functions.create_unique_id()
            loot_type = await weighted_choice([(4, 65), (5, 35)])
            component = await game_functions.get_component(loot_type)
            tier_3_loot = {'type_id': loot_type, 'id': loot_id, 'amount': tier_3_amount}
            loot.append(tier_3_loot)
            tier_3_text = '{}x {}\n'.format(tier_3_amount, component['name'])
        if tier_1 is True or tier_2 is True or tier_3 is True:
            channel = self.bot.get_user(player[2])
            await channel.send('**Ship Component Salvage Received**\n{}{}{}\n\n*Salvage stored in your ships component'
                               ' cargo bay. Dock and do !!me to see an option to empty it*'.format(tier_1_text,
                                                                                                   tier_2_text,
                                                                                                   tier_3_text))
            ship['component_cargo_bay'] = loot
            sql = ''' UPDATE eve_rpg_players
                    SET ship = (?)
                    WHERE
                        player_id = (?); '''
            values = (str(ship), player[2],)
            return await db.execute_sql(sql, values)

    async def pve_loot(self, player, chance, overseer=False, officer=False):
        false = 200 - int(chance)
        loot_drop = await weighted_choice([(True, chance), (False, false)])
        if loot_drop is True or officer is True:
            player = await game_functions.refresh_player(player)
            ship = ast.literal_eval(player[14])
            loot_type = await weighted_choice([(200, 25), (201, 25), (202, 25), (203, 25), (204, 25)])
            item = await game_functions.get_module(loot_type)
            if 'module_cargo_bay' in ship:
                loot = ship['module_cargo_bay']
                loot.append(loot_type)
            else:
                loot = [loot_type]
            channel = self.bot.get_user(player[2])
            await channel.send('**PVE Loot Received**\n\n**{}**\n\n*Get to a station and empty your module '
                               'bay to get it*'.format(item['name']))
            ship['module_cargo_bay'] = loot
            sql = ''' UPDATE eve_rpg_players
                    SET ship = (?)
                    WHERE
                        player_id = (?); '''
            values = (str(ship), player[2],)
            await db.execute_sql(sql, values)
        if overseer is True:
            player = await game_functions.refresh_player(player)
            ship = ast.literal_eval(player[14])
            loot_type = await weighted_choice([(205, 50), (206, 25), (207, 10), (208, 5)])
            item = await game_functions.get_module(loot_type)
            if 'module_cargo_bay' in ship:
                loot = ship['module_cargo_bay']
                loot.append(loot_type)
            else:
                loot = [loot_type]
            channel = self.bot.get_user(player[2])
            await channel.send('**PVE Loot Received**\n\n**{}**\n\n*Get to a station and empty your module '
                               'bay to get it*'.format(item['name']))
            ship['module_cargo_bay'] = loot
            sql = ''' UPDATE eve_rpg_players
                    SET ship = (?)
                    WHERE
                        player_id = (?); '''
            values = (str(ship), player[2],)
            await db.execute_sql(sql, values)
