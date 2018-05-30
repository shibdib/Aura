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
         3: 'Gate Camping',
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
    1: {'id': 1, 'name': 'Ibis', 'class': 1, 'attack': 1, 'defense': 1, 'maneuver': 2, 'tracking': 1,
        'image': 'https://image.eveonline.com/Render/601_128.png', 'isk': 1000},
    2: {'id': 2, 'name': 'Impairor', 'class': 1, 'attack': 1, 'defense': 1, 'maneuver': 2, 'tracking': 1,
        'image': 'https://image.eveonline.com/Render/596_128.png', 'isk': 1000},
    3: {'id': 3, 'name': 'Reaper', 'class': 1, 'attack': 1, 'defense': 1, 'maneuver': 2, 'tracking': 1,
        'image': 'https://image.eveonline.com/Render/588_128.png', 'isk': 1000},
    4: {'id': 4, 'name': 'Velator', 'class': 1, 'attack': 1, 'defense': 1, 'maneuver': 2, 'tracking': 1,
        'image': 'https://image.eveonline.com/Render/606_128.png', 'isk': 1000},
    # Frigates
    6: {'id': 6, 'name': 'Rifter', 'class': 2, 'attack': 2, 'defense': 1, 'maneuver': 7, 'tracking': 5,
        'image': 'https://image.eveonline.com/Render/587_128.png', 'isk': 593616},
    7: {'id': 7, 'name': 'Punisher', 'class': 2, 'attack': 2, 'defense': 1, 'maneuver': 8, 'tracking': 5,
        'image': 'https://image.eveonline.com/Render/597_128.png', 'isk': 618866},
    8: {'id': 8, 'name': 'Kestrel', 'class': 2, 'attack': 2, 'defense': 1, 'maneuver': 7, 'tracking': 15,
        'image': 'https://image.eveonline.com/Render/602_128.png', 'isk': 537801},
    9: {'id': 9, 'name': 'Incursus', 'class': 2, 'attack': 3, 'defense': 1, 'maneuver': 7, 'tracking': 5,
        'image': 'https://image.eveonline.com/Render/594_128.png', 'isk': 466463},
    # Ceptors
    10: {'id': 10, 'name': 'Claw', 'class': 5, 'attack': 2, 'defense': 1, 'maneuver': 12, 'tracking': 8,
         'image': 'https://image.eveonline.com/Render/11196_128.png', 'isk': 35839340},
    11: {'id': 11, 'name': 'Crusader', 'class': 5, 'attack': 2, 'defense': 1, 'maneuver': 12, 'tracking': 8,
         'image': 'https://image.eveonline.com/Render/11184_128.png', 'isk': 36111646},
    12: {'id': 12, 'name': 'Raptor', 'class': 5, 'attack': 2, 'defense': 1, 'maneuver': 12, 'tracking': 8,
         'image': 'https://image.eveonline.com/Render/11178_128.png', 'isk': 39985863},
    13: {'id': 13, 'name': 'Taranis', 'class': 5, 'attack': 2, 'defense': 1, 'maneuver': 12, 'tracking': 8,
         'image': 'https://image.eveonline.com/Render/11200_128.png', 'isk': 40005204},
    # Destroyers
    14: {'id': 14, 'name': 'Thrasher', 'class': 3, 'attack': 4, 'defense': 1, 'maneuver': 6, 'tracking': 8,
         'image': 'https://image.eveonline.com/Render/16242_128.png', 'isk': 1216084},
    15: {'id': 15, 'name': 'Catalyst', 'class': 3, 'attack': 6, 'defense': 1, 'maneuver': 6, 'tracking': 8,
         'image': 'https://image.eveonline.com/Render/16240_128.png', 'isk': 1566992},
    16: {'id': 16, 'name': 'Coercer', 'class': 3, 'attack': 4, 'defense': 1, 'maneuver': 6, 'tracking': 8,
         'image': 'https://image.eveonline.com/Render/16236_128.png', 'isk': 1574148},
    17: {'id': 17, 'name': 'Cormorant', 'class': 3, 'attack': 4, 'defense': 1, 'maneuver': 6, 'tracking': 8,
         'image': 'https://image.eveonline.com/Render/16238_128.png', 'isk': 1194783},
    # Tactical Destroyers
    18: {'id': 18, 'name': 'Confessor', 'class': 4, 'attack': 5, 'defense': 3, 'maneuver': 6, 'tracking': 8,
         'image': 'https://image.eveonline.com/Render/34317_128.png', 'isk': 48137462},
    19: {'id': 19, 'name': 'Svipul', 'class': 4, 'attack': 6, 'defense': 3, 'maneuver': 6, 'tracking': 8,
         'image': 'https://image.eveonline.com/Render/34562_128.png', 'isk': 40611697},
    20: {'id': 20, 'name': 'Jackdaw', 'class': 4, 'attack': 4, 'defense': 4, 'maneuver': 6, 'tracking': 15,
         'image': 'https://image.eveonline.com/Render/34828_128.png', 'isk': 47903251},
    21: {'id': 21, 'name': 'Hecate', 'class': 4, 'attack': 5, 'defense': 3, 'maneuver': 6, 'tracking': 8,
         'image': 'https://image.eveonline.com/Render/35683_128.png', 'isk': 57665805},
    # Faction Frigs
    50: {'id': 50, 'name': 'Republic Fleet Firetail', 'class': 2, 'attack': 2, 'defense': 2, 'maneuver': 3, 'tracking': 2,
         'image': 'https://image.eveonline.com/Render/17812_128.png', 'isk': 18063029},
    51: {'id': 51, 'name': 'Dramiel', 'class': 2, 'attack': 2, 'defense': 2, 'maneuver': 3, 'tracking': 2,
         'image': 'https://image.eveonline.com/Render/17932_128.png', 'isk': 46790226}
}

ship_classes = {
    1: 'Rookie Ship',
    2: 'Frigate',
    3: 'Destroyer',
    4: 'Tactical Destroyer',
    5: 'Interceptor',
    6: 'Mining Frigate',
}
