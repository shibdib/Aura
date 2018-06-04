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
        'image': 'https://image.eveonline.com/Type/601_64.png', 'isk': 1000, 'slots': 1},
    2: {'id': 2, 'name': 'Impairor', 'class': 1, 'attack': 1, 'defense': 1, 'maneuver': 2, 'tracking': 1,
        'image': 'https://image.eveonline.com/Type/596_64.png', 'isk': 1000, 'slots': 1},
    3: {'id': 3, 'name': 'Reaper', 'class': 1, 'attack': 1, 'defense': 1, 'maneuver': 2, 'tracking': 1,
        'image': 'https://image.eveonline.com/Type/588_64.png', 'isk': 1000, 'slots': 1},
    4: {'id': 4, 'name': 'Velator', 'class': 1, 'attack': 1, 'defense': 1, 'maneuver': 2, 'tracking': 1,
        'image': 'https://image.eveonline.com/Type/606_64.png', 'isk': 1000, 'slots': 1},
    5: {'id': 5, 'name': 'Specter', 'class': 1, 'attack': 2, 'defense': 2, 'maneuver': 2, 'tracking': 1,
        'image': 'https://image.eveonline.com/Type/606_64.png', 'isk': 1000, 'slots': 1},
    # Frigates
    6: {'id': 6, 'name': 'Rifter', 'class': 2, 'attack': 2, 'defense': 3, 'maneuver': 7, 'tracking': 5,
        'image': 'https://image.eveonline.com/Type/587_64.png', 'isk': 593616, 'slots': 2},
    7: {'id': 7, 'name': 'Punisher', 'class': 2, 'attack': 2, 'defense': 3, 'maneuver': 8, 'tracking': 5,
        'image': 'https://image.eveonline.com/Type/597_64.png', 'isk': 618866, 'slots': 2},
    8: {'id': 8, 'name': 'Kestrel', 'class': 2, 'attack': 2, 'defense': 3, 'maneuver': 7, 'tracking': 15,
        'image': 'https://image.eveonline.com/Type/602_64.png', 'isk': 537801, 'slots': 2},
    9: {'id': 9, 'name': 'Incursus', 'class': 2, 'attack': 3, 'defense': 3, 'maneuver': 7, 'tracking': 5,
        'image': 'https://image.eveonline.com/Type/594_64.png', 'isk': 466463, 'slots': 2},
    # Ceptors
    10: {'id': 10, 'name': 'Claw', 'class': 5, 'attack': 2, 'defense': 2, 'maneuver': 12, 'tracking': 8,
         'image': 'https://image.eveonline.com/Type/11196_64.png', 'isk': 35839340, 'slots': 2},
    11: {'id': 11, 'name': 'Crusader', 'class': 5, 'attack': 2, 'defense': 2, 'maneuver': 12, 'tracking': 8,
         'image': 'https://image.eveonline.com/Type/11184_64.png', 'isk': 36111646, 'slots': 2},
    12: {'id': 12, 'name': 'Raptor', 'class': 5, 'attack': 2, 'defense': 2, 'maneuver': 12, 'tracking': 8,
         'image': 'https://image.eveonline.com/Type/11178_64.png', 'isk': 39985863, 'slots': 2},
    13: {'id': 13, 'name': 'Taranis', 'class': 5, 'attack': 2, 'defense': 2, 'maneuver': 12, 'tracking': 8,
         'image': 'https://image.eveonline.com/Type/11200_64.png', 'isk': 40005204, 'slots': 2},
    # Destroyers
    14: {'id': 14, 'name': 'Thrasher', 'class': 3, 'attack': 4, 'defense': 4, 'maneuver': 6, 'tracking': 8,
         'image': 'https://image.eveonline.com/Type/16242_64.png', 'isk': 1216084, 'slots': 3},
    15: {'id': 15, 'name': 'Catalyst', 'class': 3, 'attack': 6, 'defense': 4, 'maneuver': 6, 'tracking': 8,
         'image': 'https://image.eveonline.com/Type/16240_64.png', 'isk': 1566992, 'slots': 3},
    16: {'id': 16, 'name': 'Coercer', 'class': 3, 'attack': 4, 'defense': 4, 'maneuver': 6, 'tracking': 8,
         'image': 'https://image.eveonline.com/Type/16236_64.png', 'isk': 1574148, 'slots': 3},
    17: {'id': 17, 'name': 'Cormorant', 'class': 3, 'attack': 4, 'defense': 5, 'maneuver': 6, 'tracking': 8,
         'image': 'https://image.eveonline.com/Type/16238_64.png', 'isk': 1194783, 'slots': 3},
    # Tactical Destroyers
    18: {'id': 18, 'name': 'Confessor', 'class': 4, 'attack': 5, 'defense': 6, 'maneuver': 6, 'tracking': 8,
         'image': 'https://image.eveonline.com/Type/34317_64.png', 'isk': 48137462, 'slots': 3},
    19: {'id': 19, 'name': 'Svipul', 'class': 4, 'attack': 6, 'defense': 6, 'maneuver': 6, 'tracking': 8,
         'image': 'https://image.eveonline.com/Type/34562_64.png', 'isk': 40611697, 'slots': 3},
    20: {'id': 20, 'name': 'Jackdaw', 'class': 4, 'attack': 4, 'defense': 7, 'maneuver': 6, 'tracking': 15,
         'image': 'https://image.eveonline.com/Type/34828_64.png', 'isk': 47903251, 'slots': 3},
    21: {'id': 21, 'name': 'Hecate', 'class': 4, 'attack': 5, 'defense': 6, 'maneuver': 6, 'tracking': 8,
         'image': 'https://image.eveonline.com/Type/35683_64.png', 'isk': 57665805, 'slots': 3},
    # Faction Frigs
    50: {'id': 50, 'name': 'Republic Fleet Firetail', 'class': 2, 'attack': 3, 'defense': 5, 'maneuver': 8,
         'tracking': 5,
         'image': 'https://image.eveonline.com/Type/17812_64.png', 'isk': 18063029, 'slots': 3},
    51: {'id': 51, 'name': 'Dramiel', 'class': 2, 'attack': 3, 'defense': 5, 'maneuver': 9, 'tracking': 5,
         'image': 'https://image.eveonline.com/Type/17932_64.png', 'isk': 46790226, 'slots': 3},
    # Mining frigate
    70: {'id': 70, 'name': 'Venture', 'class': 6, 'attack': 1, 'defense': 5, 'maneuver': 4, 'tracking': 1,
         'image': 'https://image.eveonline.com/Type/32880_64.png', 'isk': 593884, 'slots': 2},
    # Mining barge
    80: {'id': 80, 'name': 'Procurer', 'class': 7, 'attack': 1, 'defense': 12, 'maneuver': 1, 'tracking': 1,
         'image': 'https://image.eveonline.com/Type/17480_64.png', 'isk': 18656208, 'slots': 3},
    81: {'id': 81, 'name': 'Covetor', 'class': 7, 'attack': 1, 'defense': 6, 'maneuver': 1, 'tracking': 1,
         'image': 'https://image.eveonline.com/Type/17476_64.png', 'isk': 26888937, 'slots': 3},
    # Exhumer
    90: {'id': 90, 'name': 'Skiff', 'class': 8, 'attack': 1, 'defense': 18, 'maneuver': 2, 'tracking': 1,
         'image': 'https://image.eveonline.com/Type/22546_64.png', 'isk': 297386539, 'slots': 3},
    91: {'id': 90, 'name': 'Hulk', 'class': 8, 'attack': 1, 'defense': 8, 'maneuver': 2, 'tracking': 1,
         'image': 'https://image.eveonline.com/Type/22544_64.png', 'isk': 382481286, 'slots': 3},
}

ship_classes = {
    1: 'Rookie Ship',
    2: 'Frigate',
    3: 'Destroyer',
    4: 'Tactical Destroyer',
    5: 'Interceptor',
    6: 'Mining Frigate',
    7: 'Mining Barge',
    8: 'Exhumer',
}

modules = {  # Attack
    1: {'id': 1, 'name': 'Gyrostabilizer I', 'class': 1, 'attack': .15, 'defense': 0, 'maneuver': 0, 'tracking': .10,
        'image': 'https://image.eveonline.com/Type/520_64.png', 'isk': 51807, 'special': None},
    2: {'id': 2, 'name': 'Magnetic Field Stabilizer I', 'class': 1, 'attack': .25, 'defense': 0, 'maneuver': 0,
        'tracking': 0, 'image': 'https://image.eveonline.com/Type/9944_64.png', 'isk': 65447, 'special': None},
    3: {'id': 3, 'name': 'Tracking Enhancer I', 'class': 4, 'attack': 0, 'defense': 0, 'maneuver': 0, 'tracking': .25,
        'image': 'https://image.eveonline.com/Type/1998_64.png', 'isk': 89714, 'special': None},
    4: {'id': 4, 'name': 'Gyrostabilizer II', 'class': 1, 'attack': .25, 'defense': 0, 'maneuver': 0, 'tracking': .15,
        'image': 'https://image.eveonline.com/Type/519_64.png', 'isk': 1153795, 'special': None},
    5: {'id': 5, 'name': 'Magnetic Field Stabilizer II', 'class': 1, 'attack': .35, 'defense': 0, 'maneuver': 0,
        'tracking': 0, 'image': 'https://image.eveonline.com/Type/10190_64.png', 'isk': 1682869, 'special': None},
    6: {'id': 6, 'name': 'Tracking Enhancer II', 'class': 4, 'attack': 0, 'defense': 0, 'maneuver': 0, 'tracking': .35,
        'image': 'https://image.eveonline.com/Type/1999_64.png', 'isk': 977745, 'special': None},
    # Defense
    7: {'id': 7, 'name': 'Shield Extender I', 'class': 2, 'attack': 0, 'defense': .20, 'maneuver': 0, 'tracking': 0,
        'image': 'https://image.eveonline.com/Type/3829_64.png', 'isk': 39489, 'special': None},
    8: {'id': 8, 'name': 'Armor Plate I', 'class': 2, 'attack': 0, 'defense': .30, 'maneuver': -.10, 'tracking': 0,
        'image': 'https://image.eveonline.com/Type/11295_64.png', 'isk': 45775, 'special': None},
    9: {'id': 9, 'name': 'Nanofiber Internal Structure I', 'class': 3, 'attack': 0, 'defense': -0.05, 'maneuver': .20,
        'tracking': 0, 'image': 'https://image.eveonline.com/Type/2603_64.png', 'isk': 55014, 'special': None},
    10: {'id': 10, 'name': 'Shield Extender II', 'class': 2, 'attack': 0, 'defense': .30, 'maneuver': 0, 'tracking': 0,
         'image': 'https://image.eveonline.com/Type/3831_64.png', 'isk': 1121578, 'special': None},
    11: {'id': 11, 'name': 'Armor Plate II', 'class': 2, 'attack': 0, 'defense': .40, 'maneuver': -.15, 'tracking': 0,
         'image': 'https://image.eveonline.com/Type/20347_64.png', 'isk': 1451677, 'special': None},
    12: {'id': 12, 'name': 'Nanofiber Internal Structure II', 'class': 3, 'attack': 0, 'defense': -0.05,
         'maneuver': .30,
         'tracking': 0, 'image': 'https://image.eveonline.com/Type/2605_64.png', 'isk': 1566478, 'special': None},
    13: {'id': 13, 'name': 'MWD I', 'class': 3, 'attack': 0, 'defense': 0, 'maneuver': .30, 'tracking': -.10,
         'image': 'https://image.eveonline.com/Type/5973_64.png', 'isk': 22365, 'special': None},
    14: {'id': 14, 'name': 'AB I', 'class': 3, 'attack': 0, 'defense': 0, 'maneuver': .25, 'tracking': 0,
         'image': 'https://image.eveonline.com/Type/12056_64.png', 'isk': 20145, 'special': None},
    15: {'id': 15, 'name': 'MWD II', 'class': 3, 'attack': 0, 'defense': 0, 'maneuver': .45, 'tracking': -.15,
         'image': 'https://image.eveonline.com/Type/440_64.png', 'isk': 758662, 'special': None},
    16: {'id': 16, 'name': 'AB II', 'class': 3, 'attack': 0, 'defense': 0, 'maneuver': .35, 'tracking': 0,
         'image': 'https://image.eveonline.com/Type/12058_64.png', 'isk': 712445, 'special': None},
    17: {'id': 17, 'name': 'Mining Laser Upgrade I', 'class': 5, 'attack': 0, 'defense': 0, 'maneuver': 0,
         'tracking': 0, 'image': 'https://image.eveonline.com/Type/22542_64.png', 'isk': 29554, 'special': '10% '
                                                                                                              'Mining Bonus'},
    18: {'id': 18, 'name': 'Mining Laser Upgrade II', 'class': 5, 'attack': 0, 'defense': 0, 'maneuver': 0,
         'tracking': 0, 'image': 'https://image.eveonline.com/Type/28576_64.png', 'isk': 287445, 'special': '20% '
                                                                                                               'Mining Bonus'},
}

components = {
    # Junk tier 1
    1: {'id': 1, 'name': 'Metal Scraps', 'image': 'https://image.eveonline.com/Type/15331_64.png', 'isk': 1960},
    # Junk tier 2
    2: {'id': 2, 'name': 'Burned Logic Circuit', 'image': 'https://image.eveonline.com/Type/25600_64.png',
        'isk': 77198},
    3: {'id': 3, 'name': 'Armor Plates', 'image': 'https://image.eveonline.com/Type/25605_64.png', 'isk': 47239},
    # Junk tier 3
    4: {'id': 4, 'name': 'Intact Shield Emitter', 'image': 'https://image.eveonline.com/Type/25608_64.png',
        'isk': 1213453},
    5: {'id': 5, 'name': 'Intact Armor Plates', 'image': 'https://image.eveonline.com/Type/25624_64.png',
        'isk': 5797061},
}
