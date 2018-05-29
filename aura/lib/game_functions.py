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
                      4: [1, 2, 3, 8]}

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
         10: 'Anomaly Mining'}


async def get_region(region_id):
    return regions[region_id]


async def get_region_connections(region_id):
    return region_connections[region_id]


async def get_task(task_id):
    return tasks[task_id]
