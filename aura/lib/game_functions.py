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


async def get_combat_attributes(ship_id):
    ship = game_assets.ships[ship_id]
    return ship['attack'], ship['defense'], ship['maneuver'], ship['tracking']
