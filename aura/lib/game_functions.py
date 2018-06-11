import ast
import random

from aura.lib import db
from aura.lib import game_assets


async def tick_count():
    sql = ''' SELECT int FROM data WHERE `entry` = 'tick_number' '''
    current_tick_array = await db.select(sql)
    current_tick = None
    if len(current_tick_array) > 0:
        current_tick = int(current_tick_array[0][0])
    if current_tick is None:
        current_tick = 0
    current_tick += 1
    sql = ''' REPLACE INTO data(entry,int)
              VALUES(?,?) '''
    values = ('tick_number', current_tick)
    await db.execute_sql(sql, values)
    return current_tick


async def combat_timer_management():
    sql = ''' SELECT * FROM eve_rpg_players WHERE `combat_timer` > (?) '''
    values = (0,)
    timer_players = await db.select_var(sql, values)
    if len(timer_players) == 0:
        return
    for player in timer_players:
        new_timer = player[25] - 1
        if new_timer <= 0:
            new_timer = None
        sql = ''' UPDATE eve_rpg_players
                SET combat_timer = (?)
                WHERE
                    player_id = (?); '''
        values = (new_timer, player[2],)
        await db.execute_sql(sql, values)


async def refresh_player(player):
    sql = ''' SELECT * FROM eve_rpg_players WHERE `player_id` = (?) '''
    values = (player[2],)
    new_player = await db.select_var(sql, values)
    return new_player[0]


async def get_region(region_id):
    return game_assets.regions[region_id]


async def get_region_connections(region_id):
    return game_assets.region_connections[region_id]


async def get_region_security(region_id):
    return game_assets.region_security[region_id]


async def get_task(task_id):
    return game_assets.tasks[task_id]


async def get_ship(ship_id):
    try:
        return game_assets.ships[ship_id]
    except Exception:
        return None


async def get_module(module_id):
    try:
        return game_assets.modules[module_id]
    except Exception:
        return None


async def get_component(component_id):
    try:
        return game_assets.components[component_id]
    except Exception:
        return None


async def get_ship_name(ship_id):
    return game_assets.ships[ship_id]['name']


async def get_module_name(module_id):
    try:
        return game_assets.modules[module_id]['name']
    except Exception:
        return None


async def get_ship_image(ship_id):
    return game_assets.ships[ship_id]['image']


async def get_npc(sec):
    possible_npc = []
    for key, npc in game_assets.npc.items():
        if sec < 10:
            if npc['class'] <= sec:
                possible_npc.append(npc)
        else:
            if npc['class'] == sec:
                possible_npc.append(npc)
    if len(possible_npc) > 0:
        return random.choice(possible_npc)
    else:
        return None


async def get_combat_attributes(player, ship_id, npc=False):
    if npc is False:
        ship = game_assets.ships[ship_id]
        attack = int(ship['attack'])
        defense = int(ship['defense'])
        maneuver = int(ship['maneuver'])
        tracking = int(ship['tracking'])
        if player[12] is not None:
            equipped_modules = ast.literal_eval(player[12])
            checked_modules = []
            for item in equipped_modules:
                module = await get_module(int(item))
                checked_modules.append(module['class'])
                current_count = checked_modules.count(module['class'])
                efficiency = 1
                if current_count > 1:
                    efficiency = 1 - (0.5 * (0.45 * (current_count - 1)) ** 2)
                if 'size' not in module:
                    attack = int(float((attack * (module['attack'] * efficiency)) + attack))
                    defense = int(float((defense * (module['defense'] * efficiency)) + defense))
                    maneuver = int(float((maneuver * (module['maneuver'] * efficiency)) + maneuver))
                    tracking = int(float((tracking * (module['tracking'] * efficiency)) + tracking))
            for item in equipped_modules:
                module = await get_module(int(item))
                if 'size' in module:
                    attack = module['attack'] + attack
                    defense = module['defense'] + defense
                    maneuver = module['maneuver'] + maneuver
                    tracking = module['tracking'] + tracking
    else:
        ship = game_assets.npc[ship_id]
        attack = int(ship['attack'])
        defense = int(ship['defense'])
        maneuver = int(ship['maneuver'])
        tracking = int(ship['tracking'])
    return int(round(attack)), int(round(defense)), int(round(maneuver)), int(round(tracking))


async def get_mission(level):
    possible_missions = []
    for key, mission in game_assets.missions.items():
        if mission['level'] == int(level):
            possible_missions.append(mission)
    if len(possible_missions) > 0:
        return random.choice(possible_missions)
    return None


async def create_unique_id():
    sql = ''' SELECT int FROM data WHERE `entry` = 'current_id' '''
    current_id_array = await db.select(sql)
    current_id = int(current_id_array[0][0])
    if current_id is None:
        current_id = 0
    current_id += 1
    sql = ''' REPLACE INTO data(entry,int)
              VALUES(?,?) '''
    values = ('current_id', current_id)
    await db.execute_sql(sql, values)
    return current_id


async def get_user_corp(corp_id):
    sql = ''' SELECT * FROM corporations WHERE `corp_id` = (?) '''
    values = (corp_id,)
    corp_info = await db.select_var(sql, values)
    if len(corp_info) > 0:
        return corp_info[0]
    else:
        return None
