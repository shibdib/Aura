import ast

from aura.lib import db
from aura.lib import game_assets


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


async def get_ship_name(ship_id):
    return game_assets.ships[ship_id]['name']


async def get_module_name(module_id):
    try:
        return game_assets.modules[module_id]['name']
    except Exception:
        return None


async def get_ship_image(ship_id):
    return game_assets.ships[ship_id]['image']


async def get_combat_attributes(player, ship_id):
    ship = game_assets.ships[ship_id]
    attack = int(ship['attack'])
    defense = int(ship['defense'])
    maneuver = int(ship['maneuver'])
    tracking = int(ship['tracking'])
    if player[12] is not None:
        equipped_modules = ast.literal_eval(player[12])
        for item in equipped_modules:
            module = await get_module(int(item))
            attack = (attack * module['attack']) + attack
            defense = (defense * module['defense']) + defense
            maneuver = (maneuver * module['maneuver']) + maneuver
            tracking = (tracking * module['tracking']) + tracking
    return int(round(attack)), int(round(defense)), int(round(maneuver)), int(round(tracking))


async def create_unique_id():
    sql = ''' SELECT int FROM data WHERE `entry` = 'current_id' '''
    current_id = await db.select(sql)
    if current_id is None:
        current_id = 0
    next_id = current_id + 1
    sql = ''' REPLACE INTO data(entry,int)
              VALUES(?,?) '''
    values = ('current_id', next_id)
    await db.execute_sql(sql, values)
    return next_id
