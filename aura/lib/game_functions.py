import json
import aiohttp

regions = {1: 'The Forge',
           2: 'Domain',
           3: 'Heimatar',
           4: 'Essence'}

tasks = {0: 'Docked',
         # PVP
         2: 'Roaming',
         3: 'Gate Camp',
         4: 'Ganking',
         5: 'Fleet Roam',
         # PVE
         6: 'Killing Belt Rats',
         7: 'Running Anomalies',
         8: 'Exploring',
         9: 'Belt Mining',
         10: 'Anomaly Mining'}

focuses = {0: 'Dev',
         # PVP
         1: 'PVP',
         # PVE
         2: 'PVE',
         3: 'Mining',
         4: 'Industry'}


async def get_region(region_id):
    return regions[region_id]


async def get_task(task_id):
    return tasks[task_id]


async def get_focus(focus_id):
    return focuses[focus_id]
