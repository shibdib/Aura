regions = {1: 'The Forge',
           2: 'Domain',
           3: 'Heimatar',
           4: 'Essence',
           # low
           5: 'Lonetrek',
           6: 'Solitude',
           7: 'Aridia',
           8: 'Derelik',
           # null
           9: 'Venal',
           10: 'Fountain',
           11: 'Delve',
           12: 'Catch'}

region_connections = {1: [2, 3, 4, 5],
                      2: [1, 3, 4, 6],
                      3: [1, 2, 4, 7],
                      4: [1, 2, 3, 8],
                      5: [1, 9],
                      6: [2, 10],
                      7: [3, 11],
                      8: [4, 12],
                      9: [5, 10, 12],
                      10: [6, 9, 11],
                      11: [7, 10, 12],
                      12: [8, 9, 11]}

region_security = {1: 'High',
                   2: 'High',
                   3: 'High',
                   4: 'High',
                   # low
                   5: 'Low',
                   6: 'Low',
                   7: 'Low',
                   8: 'Low',
                   # null
                   9: 'Null',
                   10: 'Null',
                   11: 'Null',
                   12: 'Null'}

tasks = {1: 'Docked',
         # PVP
         2: 'Roaming',
         3: 'Gate Camp',
         4: 'Ganking',
         5: 'Fleet Roam',
         # PVE
         6: 'Killing Belt Rats',
         7: 'Running Anomalies',
         8: 'Exploring',
         # MINING
         9: 'Belt Mining',
         10: 'Anomaly Mining',
         # GENERIC
         20: 'Traveling',
         21: 'In Space'}

ships = {  # Noob
    1: {'name': 'Ibis', 'attack': 1, 'defense': 1, 'maneuver': 2, 'tracking': 1},
    2: {'name': 'Impairor', 'attack': 1, 'defense': 1, 'maneuver': 2, 'tracking': 1},
    3: {'name': 'Reaper', 'attack': 1, 'defense': 1, 'maneuver': 2, 'tracking': 1},
    4: {'name': 'Velator', 'attack': 1, 'defense': 1, 'maneuver': 2, 'tracking': 1},
    5: {'name': 'Specter', 'attack': 2, 'defense': 2, 'maneuver': 3, 'tracking': 2},
    # Frigates
    6: {'name': 'Rifter', 'attack': 2, 'defense': 1, 'maneuver': 7, 'tracking': 5},
    7: {'name': 'Slicer', 'attack': 2, 'defense': 1, 'maneuver': 8, 'tracking': 5},
    8: {'name': 'Kestrel', 'attack': 2, 'defense': 1, 'maneuver': 7, 'tracking': 15},
    9: {'name': 'Incursus', 'attack': 3, 'defense': 1, 'maneuver': 7, 'tracking': 5},
    # Ceptors
    10: {'name': 'Claw', 'attack': 2, 'defense': 1, 'maneuver': 12, 'tracking': 8},
    11: {'name': 'Crusader', 'attack': 2, 'defense': 1, 'maneuver': 12, 'tracking': 8},
    12: {'name': 'Raptor', 'attack': 2, 'defense': 1, 'maneuver': 12, 'tracking': 8},
    13: {'name': 'Taranis', 'attack': 2, 'defense': 1, 'maneuver': 12, 'tracking': 8},
    # Destroyers
    14: {'name': 'Thrasher', 'attack': 4, 'defense': 1, 'maneuver': 6, 'tracking': 8},
    15: {'name': 'Catalyst', 'attack': 6, 'defense': 1, 'maneuver': 6, 'tracking': 8},
    16: {'name': 'Coercer', 'attack': 4, 'defense': 1, 'maneuver': 6, 'tracking': 8},
    17: {'name': 'Cormorant', 'attack': 4, 'defense': 1, 'maneuver': 6, 'tracking': 8},
    # Tactical Destroyers
    18: {'name': 'Confessor', 'attack': 5, 'defense': 3, 'maneuver': 6, 'tracking': 8},
    19: {'name': 'Svipul', 'attack': 6, 'defense': 3, 'maneuver': 6, 'tracking': 8},
    20: {'name': 'Jackdaw', 'attack': 4, 'defense': 4, 'maneuver': 6, 'tracking': 15},
    21: {'name': 'Hecate', 'attack': 5, 'defense': 3, 'maneuver': 6, 'tracking': 8},
    # Faction Frigs
    50: {'name': 'Firetail', 'attack': 2, 'defense': 2, 'maneuver': 3, 'tracking': 2},
    51: {'name': 'Dramiel', 'attack': 2, 'defense': 2, 'maneuver': 3, 'tracking': 2}}

async def get_region(region_id):
    return regions[region_id]


async def get_region_connections(region_id):
    return region_connections[region_id]


async def get_region_security(region_id):
    return region_security[region_id]


async def get_task(task_id):
    return tasks[task_id]


async def get_ship(ship_id):
    return ships[ship_id]


async def get_combat_attributes(ship_id):
    ship = ships[ship_id]
    return ship['attack'], ship['defense'], ship['maneuver'], ship['tracking']
