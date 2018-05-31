import ast

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
    module_attack = 0
    module_defense = 0
    module_maneuver = 0
    module_tracking = 0
    if player[12] is not None:
        equipped_modules = ast.literal_eval(player[12])
        for item in equipped_modules:
            module = await get_module(int(item))
            module_attack += module['attack']
            module_defense += module['defense']
            module_maneuver += module['maneuver']
            module_tracking += module['tracking']
    attack = int(ship['attack']) + module_attack
    defense = int(ship['defense']) + module_defense
    maneuver = int(ship['maneuver']) + module_maneuver
    tracking = int(ship['tracking']) + module_tracking
    return attack, defense, maneuver, tracking
