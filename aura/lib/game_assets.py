regions = {1: 'The Forge',
           2: 'Domain',
           3: 'Heimatar',
           4: 'Essence',
           # low
           5: 'Lonetrek',
           6: 'Solitude',
           7: 'Aridia',
           8: 'Derelik',
           17: 'Placid',
           18: 'Khanid',
           19: 'Devoid',
           20: 'Metropolis',
           # null
           9: 'Venal',
           10: 'Fountain',
           11: 'Delve',
           12: 'Catch',
           13: 'Insmother',
           14: 'Outer Passage',
           15: 'Deklein',
           16: 'Cloud Ring'}

region_connections = {1: [2, 3, 4, 5, 20],
                      2: [1, 3, 4, 6, 19],
                      3: [1, 2, 4, 7, 19, 20],
                      4: [1, 2, 3, 8],
                      5: [1, 9, 17],
                      6: [2, 10, 17],
                      7: [3, 10, 11, 18],
                      8: [4, 12, 19],
                      9: [5, 10, 12],
                      10: [6, 7, 9, 11, 16],
                      11: [7, 10, 12],
                      12: [8, 9, 11, 13, 18, 19],
                      13: [12, 14],
                      14: [13, 15],
                      15: [14, 16],
                      16: [10, 15, 17],
                      17: [5, 6, 16],
                      18: [7, 12],
                      19: [2, 3, 8, 12],
                      20: [1, 3]}

region_security = {1: 'High',
                   2: 'High',
                   3: 'High',
                   4: 'High',
                   # low
                   5: 'Low',
                   6: 'Low',
                   7: 'Low',
                   8: 'Low',
                   17: 'Low',
                   18: 'Low',
                   19: 'Low',
                   20: 'Low',
                   # null
                   9: 'Null',
                   10: 'Null',
                   11: 'Null',
                   12: 'Null',
                   13: 'Null',
                   14: 'Null',
                   15: 'Null',
                   16: 'Null'}

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
         9: 'Running a Mission Site',
         # MINING
         10: 'Belt Mining',
         11: 'Anomaly Mining',
         # GENERIC
         20: 'Traveling',
         21: 'In Space'}

ships = {  # Noob
    1: {'id': 1, 'name': 'Ibis', 'class': 0, 'hit_points': 2, 'attack': 1, 'defense': 1, 'maneuver': 2, 'tracking': 12,
        'image': 'https://image.eveonline.com/Type/601_64.png', 'pve_multi': 0.1, 'isk': 1000, 'slots': 1,
        'drone_bay': 0},
    2: {'id': 2, 'name': 'Impairor', 'class': 0, 'hit_points': 2, 'attack': 1, 'defense': 1, 'maneuver': 2,
        'tracking': 12,
        'image': 'https://image.eveonline.com/Type/596_64.png', 'pve_multi': 0.1, 'isk': 1000, 'slots': 1,
        'drone_bay': 0},
    3: {'id': 3, 'name': 'Reaper', 'class': 0, 'hit_points': 2, 'attack': 1, 'defense': 1, 'maneuver': 2,
        'tracking': 12,
        'image': 'https://image.eveonline.com/Type/588_64.png', 'pve_multi': 0.1, 'isk': 1000, 'slots': 1,
        'drone_bay': 0},
    4: {'id': 4, 'name': 'Velator', 'class': 0, 'hit_points': 2, 'attack': 1, 'defense': 1, 'maneuver': 2,
        'tracking': 12,
        'image': 'https://image.eveonline.com/Type/606_64.png', 'pve_multi': 0.1, 'isk': 1000, 'slots': 1,
        'drone_bay': 0},
    5: {'id': 5, 'name': 'Specter', 'class': 0, 'hit_points': 2, 'attack': 2, 'defense': 2, 'maneuver': 2,
        'tracking': 13,
        'image': 'https://image.eveonline.com/Type/606_64.png', 'pve_multi': 0.1, 'isk': 1000, 'slots': 1,
        'drone_bay': 0},
    # Frigates
    6: {'id': 6, 'name': 'Rifter', 'class': 1, 'hit_points': 3, 'attack': 2, 'defense': 3, 'maneuver': 7,
        'tracking': 16,
        'image': 'https://image.eveonline.com/Type/587_64.png', 'pve_multi': 1.5, 'isk': 593616, 'slots': 2,
        'drone_bay': 0},
    7: {'id': 7, 'name': 'Punisher', 'class': 1, 'hit_points': 3, 'attack': 2, 'defense': 3, 'maneuver': 8,
        'tracking': 16,
        'image': 'https://image.eveonline.com/Type/597_64.png', 'pve_multi': 1.5, 'isk': 618866, 'slots': 2,
        'drone_bay': 0},
    8: {'id': 8, 'name': 'Kestrel', 'class': 1, 'hit_points': 3, 'attack': 2, 'defense': 4, 'maneuver': 7,
        'tracking': 25,
        'image': 'https://image.eveonline.com/Type/602_64.png', 'pve_multi': 1.5, 'isk': 537801, 'slots': 2,
        'drone_bay': 0},
    9: {'id': 9, 'name': 'Tristan', 'class': 1, 'hit_points': 3, 'attack': 1, 'defense': 3, 'maneuver': 7,
        'tracking': 17,
        'image': 'https://image.eveonline.com/Type/593_64.png', 'pve_multi': 1.5, 'isk': 855239, 'slots': 2,
        'drone_bay': 5},
    # Ceptors
    10: {'id': 10, 'name': 'Claw', 'class': 2, 'hit_points': 3, 'attack': 3, 'defense': 2, 'maneuver': 12,
         'tracking': 18,
         'image': 'https://image.eveonline.com/Type/11196_64.png', 'pve_multi': 1, 'isk': 35839340, 'slots': 2,
         'drone_bay': 0},
    11: {'id': 11, 'name': 'Crusader', 'class': 2, 'hit_points': 3, 'attack': 2, 'defense': 2, 'maneuver': 14,
         'tracking': 19,
         'image': 'https://image.eveonline.com/Type/11184_64.png', 'pve_multi': 1, 'isk': 36111646, 'slots': 2,
         'drone_bay': 0},
    12: {'id': 12, 'name': 'Raptor', 'class': 2, 'hit_points': 3, 'attack': 2, 'defense': 3, 'maneuver': 12,
         'tracking': 19,
         'image': 'https://image.eveonline.com/Type/11178_64.png', 'pve_multi': 1, 'isk': 39985863, 'slots': 2,
         'drone_bay': 0},
    13: {'id': 13, 'name': 'Taranis', 'class': 2, 'hit_points': 3, 'attack': 3, 'defense': 2, 'maneuver': 13,
         'tracking': 20,
         'image': 'https://image.eveonline.com/Type/11200_64.png', 'pve_multi': 1, 'isk': 40005204, 'slots': 2,
         'drone_bay': 0},
    # Destroyers
    14: {'id': 14, 'name': 'Thrasher', 'class': 3, 'hit_points': 5, 'attack': 6, 'defense': 5, 'maneuver': 6,
         'tracking': 15,
         'image': 'https://image.eveonline.com/Type/16242_64.png', 'pve_multi': 3, 'isk': 1216084, 'slots': 3,
         'drone_bay': 0},
    15: {'id': 15, 'name': 'Catalyst', 'class': 3, 'hit_points': 5, 'attack': 7, 'defense': 5, 'maneuver': 6,
         'tracking': 13,
         'image': 'https://image.eveonline.com/Type/16240_64.png', 'pve_multi': 3, 'isk': 1566992, 'slots': 3,
         'drone_bay': 0},
    16: {'id': 16, 'name': 'Coercer', 'class': 3, 'hit_points': 5, 'attack': 6, 'defense': 5, 'maneuver': 6,
         'tracking': 14,
         'image': 'https://image.eveonline.com/Type/16236_64.png', 'pve_multi': 3, 'isk': 1574148, 'slots': 3,
         'drone_bay': 0},
    17: {'id': 17, 'name': 'Cormorant', 'class': 3, 'hit_points': 5, 'attack': 6, 'defense': 6, 'maneuver': 6,
         'tracking': 15,
         'image': 'https://image.eveonline.com/Type/16238_64.png', 'pve_multi': 3, 'isk': 1194783, 'slots': 3,
         'drone_bay': 0},
    # Tactical Destroyers
    18: {'id': 18, 'name': 'Confessor', 'class': 4, 'hit_points': 6, 'attack': 13, 'defense': 10, 'maneuver': 6,
         'tracking': 15,
         'image': 'https://image.eveonline.com/Type/34317_64.png', 'pve_multi': 3.5, 'isk': 48137462, 'slots': 4,
         'drone_bay': 0},
    19: {'id': 19, 'name': 'Svipul', 'class': 4, 'hit_points': 6, 'attack': 15, 'defense': 10, 'maneuver': 6,
         'tracking': 16,
         'image': 'https://image.eveonline.com/Type/34562_64.png', 'pve_multi': 3.5, 'isk': 40611697, 'slots': 4,
         'drone_bay': 0},
    20: {'id': 20, 'name': 'Jackdaw', 'class': 4, 'hit_points': 6, 'attack': 12, 'defense': 11, 'maneuver': 6,
         'tracking': 30,
         'image': 'https://image.eveonline.com/Type/34828_64.png', 'pve_multi': 3.5, 'isk': 47903251, 'slots': 4,
         'drone_bay': 0},
    21: {'id': 21, 'name': 'Hecate', 'class': 4, 'hit_points': 6, 'attack': 13, 'defense': 10, 'maneuver': 6,
         'tracking': 17,
         'image': 'https://image.eveonline.com/Type/35683_64.png', 'pve_multi': 3.5, 'isk': 57665805, 'slots': 4,
         'drone_bay': 0},
    # Cruisers
    22: {'id': 22, 'name': 'Omen', 'class': 5, 'hit_points': 8, 'attack': 12, 'defense': 10, 'maneuver': 4,
         'tracking': 10,
         'image': 'https://image.eveonline.com/Type/2006_64.png', 'pve_multi': 5, 'isk': 9385386, 'slots': 4,
         'drone_bay': 5},
    23: {'id': 23, 'name': 'Rupture', 'class': 5, 'hit_points': 9, 'attack': 11, 'defense': 11, 'maneuver': 3,
         'tracking': 11,
         'image': 'https://image.eveonline.com/Type/629_64.png', 'pve_multi': 5, 'isk': 10143856, 'slots': 4,
         'drone_bay': 10},
    24: {'id': 24, 'name': 'Caracal', 'class': 5, 'hit_points': 8, 'attack': 11, 'defense': 8, 'maneuver': 4,
         'tracking': 25,
         'image': 'https://image.eveonline.com/Type/621_64.png', 'pve_multi': 5, 'isk': 10129608, 'slots': 4,
         'drone_bay': 10},
    25: {'id': 25, 'name': 'Vexor', 'class': 5, 'hit_points': 10, 'attack': 4, 'defense': 9, 'maneuver': 4,
         'tracking': 13,
         'image': 'https://image.eveonline.com/Type/626_64.png', 'pve_multi': 7.5, 'isk': 9514099, 'slots': 4,
         'drone_bay': 25},
    # Battle Cruisers
    26: {'id': 26, 'name': 'Prophecy', 'class': 6, 'hit_points': 15, 'attack': 15, 'defense': 18, 'maneuver': 3,
         'tracking': 8,
         'image': 'https://image.eveonline.com/Type/16233_64.png', 'pve_multi': 8, 'isk': 52033514, 'slots': 4,
         'drone_bay': 50},
    27: {'id': 27, 'name': 'Harbinger', 'class': 6, 'hit_points': 13, 'attack': 17, 'defense': 15, 'maneuver': 3,
         'tracking': 9,
         'image': 'https://image.eveonline.com/Type/24696_64.png', 'pve_multi': 6, 'isk': 49935988, 'slots': 4,
         'drone_bay': 15},
    28: {'id': 28, 'name': 'Ferox', 'class': 6, 'hit_points': 13, 'attack': 16, 'defense': 16, 'maneuver': 3,
         'tracking': 9,
         'image': 'https://image.eveonline.com/Type/16227_64.png', 'pve_multi': 6, 'isk': 44752064, 'slots': 4,
         'drone_bay': 15},
    29: {'id': 29, 'name': 'Drake', 'class': 6, 'hit_points': 16, 'attack': 14, 'defense': 20, 'maneuver': 3,
         'tracking': 20,
         'image': 'https://image.eveonline.com/Type/24698_64.png', 'pve_multi': 8, 'isk': 47192322, 'slots': 4,
         'drone_bay': 10},
    30: {'id': 30, 'name': 'Brutix', 'class': 6, 'hit_points': 13, 'attack': 18, 'defense': 13, 'maneuver': 3,
         'tracking': 8,
         'image': 'https://image.eveonline.com/Type/16229_64.png', 'pve_multi': 6, 'isk': 50660988, 'slots': 4,
         'drone_bay': 10},
    31: {'id': 31, 'name': 'Myrmidon', 'class': 6, 'hit_points': 14, 'attack': 10, 'defense': 15, 'maneuver': 3,
         'tracking': 9,
         'image': 'https://image.eveonline.com/Type/24700_64.png', 'pve_multi': 7, 'isk': 51235175, 'slots': 4,
         'drone_bay': 50},
    32: {'id': 32, 'name': 'Cyclone', 'class': 6, 'hit_points': 15, 'attack': 15, 'defense': 15, 'maneuver': 4,
         'tracking': 20,
         'image': 'https://image.eveonline.com/Type/16231_64.png', 'pve_multi': 6, 'isk': 45115663, 'slots': 4,
         'drone_bay': 10},
    33: {'id': 33, 'name': 'Hurricane', 'class': 6, 'hit_points': 13, 'attack': 16, 'defense': 13, 'maneuver': 5,
         'tracking': 9,
         'image': 'https://image.eveonline.com/Type/24702_64.png', 'pve_multi': 6, 'isk': 48580965, 'slots': 4,
         'drone_bay': 25},
    34: {'id': 34, 'name': 'Oracle', 'class': 6, 'hit_points': 5, 'attack': 22, 'defense': 6, 'maneuver': 3,
         'tracking': 5,
         'image': 'https://image.eveonline.com/Type/4302_64.png', 'pve_multi': 4, 'isk': 73777493, 'slots': 4,
         'drone_bay': 0},
    35: {'id': 35, 'name': 'Naga', 'class': 6, 'hit_points': 6, 'attack': 20, 'defense': 8, 'maneuver': 4,
         'tracking': 6,
         'image': 'https://image.eveonline.com/Type/4306_64.png', 'pve_multi': 3, 'isk': 66074515, 'slots': 4,
         'drone_bay': 0},
    36: {'id': 36, 'name': 'Talos', 'class': 6, 'hit_points': 5, 'attack': 25, 'defense': 5, 'maneuver': 4,
         'tracking': 5,
         'image': 'https://image.eveonline.com/Type/4308_64.png', 'pve_multi': 3, 'isk': 72734231, 'slots': 4,
         'drone_bay': 5},
    37: {'id': 37, 'name': 'Tornado', 'class': 6, 'hit_points': 5, 'attack': 23, 'defense': 5, 'maneuver': 5,
         'tracking': 5,
         'image': 'https://image.eveonline.com/Type/4310_64.png', 'pve_multi': 4, 'isk': 63533277, 'slots': 4,
         'drone_bay': 0},
    # Faction Frigs
    50: {'id': 50, 'name': 'Republic Fleet Firetail', 'class': 1, 'hit_points': 4, 'attack': 4, 'defense': 5,
         'maneuver': 8,
         'tracking': 15,
         'image': 'https://image.eveonline.com/Type/17812_64.png', 'pve_multi': 2, 'isk': 18063029, 'slots': 3,
         'drone_bay': 0},
    51: {'id': 51, 'name': 'Dramiel', 'class': 1, 'hit_points': 3, 'attack': 2, 'defense': 5, 'maneuver': 9,
         'tracking': 15,
         'image': 'https://image.eveonline.com/Type/17932_64.png', 'pve_multi': 2, 'isk': 46790226, 'slots': 3,
         'drone_bay': 5},
    # Mining frigate
    70: {'id': 70, 'name': 'Venture', 'class': 21, 'hit_points': 5, 'attack': 0, 'defense': 5, 'maneuver': 6,
         'tracking': 1,
         'image': 'https://image.eveonline.com/Type/32880_64.png', 'pve_multi': 4, 'isk': 593884, 'slots': 3,
         'drone_bay': 5},
    # Mining barge
    80: {'id': 80, 'name': 'Procurer', 'class': 22, 'hit_points': 12, 'attack': 0, 'defense': 12, 'maneuver': 1,
         'tracking': 3,
         'image': 'https://image.eveonline.com/Type/17480_64.png', 'pve_multi': 6, 'isk': 18656208, 'slots': 4,
         'drone_bay': 25},
    81: {'id': 81, 'name': 'Covetor', 'class': 22, 'hit_points': 7, 'attack': 0, 'defense': 6, 'maneuver': 1,
         'tracking': 1,
         'image': 'https://image.eveonline.com/Type/17476_64.png', 'pve_multi': 2, 'isk': 26888937, 'slots': 4,
         'drone_bay': 10},
    # Exhumer
    90: {'id': 90, 'name': 'Skiff', 'class': 23, 'hit_points': 20, 'attack': 0, 'defense': 18, 'maneuver': 2,
         'tracking': 3,
         'image': 'https://image.eveonline.com/Type/22546_64.png', 'pve_multi': 9, 'isk': 297386539, 'slots': 5,
         'drone_bay': 50},
    91: {'id': 90, 'name': 'Hulk', 'class': 23, 'hit_points': 9, 'attack': 0, 'defense': 8, 'maneuver': 2,
         'tracking': 1,
         'image': 'https://image.eveonline.com/Type/22544_64.png', 'pve_multi': 3, 'isk': 382481286, 'slots': 5,
         'drone_bay': 25},
}

ship_classes = {
    0: 'Rookie Ship',
    1: 'Frigate',
    2: 'Interceptor',
    3: 'Destroyer',
    4: 'Tactical Destroyer',
    5: 'Cruiser',
    6: 'Battlecruiser',
    21: 'Mining Frigate',
    22: 'Mining Barge',
    23: 'Exhumer',
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
    9: {'id': 9, 'name': 'Nanofiber Internal Structure I', 'class': 2, 'attack': 0, 'defense': -0.05, 'maneuver': .20,
        'tracking': 0, 'image': 'https://image.eveonline.com/Type/2603_64.png', 'isk': 55014, 'special': None},
    10: {'id': 10, 'name': 'Shield Extender II', 'class': 2, 'attack': 0, 'defense': .30, 'maneuver': 0, 'tracking': 0,
         'image': 'https://image.eveonline.com/Type/3831_64.png', 'isk': 1121578, 'special': None},
    11: {'id': 11, 'name': 'Armor Plate II', 'class': 2, 'attack': 0, 'defense': .40, 'maneuver': -.15, 'tracking': 0,
         'image': 'https://image.eveonline.com/Type/20347_64.png', 'isk': 1451677, 'special': None},
    12: {'id': 12, 'name': 'Nanofiber Internal Structure II', 'class': 2, 'attack': 0, 'defense': -0.05,
         'maneuver': .30,
         'tracking': 0, 'image': 'https://image.eveonline.com/Type/2605_64.png', 'isk': 1566478, 'special': None},
    13: {'id': 13, 'name': 'Microwarpdrive I', 'class': 3, 'attack': 0, 'defense': 0, 'maneuver': .30, 'tracking': -.10,
         'image': 'https://image.eveonline.com/Type/5973_64.png', 'isk': 22365, 'special': None},
    14: {'id': 14, 'name': 'Afterburner I', 'class': 3, 'attack': 0, 'defense': 0, 'maneuver': .25, 'tracking': 0,
         'image': 'https://image.eveonline.com/Type/12056_64.png', 'isk': 20145, 'special': None},
    15: {'id': 15, 'name': 'Microwarpdrive II', 'class': 3, 'attack': 0, 'defense': 0, 'maneuver': .45,
         'tracking': -.15,
         'image': 'https://image.eveonline.com/Type/440_64.png', 'isk': 758662, 'special': None},
    16: {'id': 16, 'name': 'Afterburner II', 'class': 3, 'attack': 0, 'defense': 0, 'maneuver': .35, 'tracking': 0,
         'image': 'https://image.eveonline.com/Type/12058_64.png', 'isk': 712445, 'special': None},
    # Mining
    17: {'id': 17, 'name': 'Mining Laser Upgrade I', 'class': 5, 'attack': 0, 'defense': 0, 'maneuver': 0,
         'tracking': 0, 'image': 'https://image.eveonline.com/Type/22542_64.png', 'isk': 29554,
         'special': '10% Mining Bonus'},
    18: {'id': 18, 'name': 'Mining Laser Upgrade II', 'class': 5, 'attack': 0, 'defense': 0, 'maneuver': 0,
         'tracking': 0, 'image': 'https://image.eveonline.com/Type/28576_64.png', 'isk': 287445,
         'special': '20% Mining Bonus'},
    # Special
    40: {'id': 40, 'name': 'Prototype Cloaking Device I', 'class': 6, 'attack': -0.1, 'defense': -0.1, 'maneuver': -0.1,
         'tracking': -0.1, 'image': 'https://image.eveonline.com/Type/11370_64.png', 'isk': 1469873,
         'special': '50% PVP Escape Bonus'},
    41: {'id': 41, 'name': 'Improved Cloaking Device II', 'class': 6, 'attack': -0.05, 'defense': -0.05,
         'maneuver': -0.05,
         'tracking': -0.05, 'image': 'https://image.eveonline.com/Type/11577_64.png', 'isk': 2696168,
         'special': '50% PVP Escape Bonus'},
    # Light
    101: {'id': 101, 'name': 'Warrior I', 'class': 10, 'attack': 0.75, 'defense': 0, 'maneuver': 2, 'tracking': 2,
          'image': 'https://image.eveonline.com/Type/2486_64.png', 'isk': 7111, 'special': None, 'size': 5},
    102: {'id': 102, 'name': 'Hobgoblin I', 'class': 10, 'attack': 2, 'defense': 0, 'maneuver': 1, 'tracking': 1,
          'image': 'https://image.eveonline.com/Type/2454_64.png', 'isk': 5060, 'special': None, 'size': 5},
    103: {'id': 103, 'name': 'Hornet I', 'class': 10, 'attack': 1, 'defense': 0, 'maneuver': 1.5, 'tracking': 1,
          'image': 'https://image.eveonline.com/Type/2464_64.png', 'isk': 4020, 'special': None, 'size': 5},
    104: {'id': 104, 'name': 'Acolyte I', 'class': 10, 'attack': 1, 'defense': 0, 'maneuver': 1.5, 'tracking': 1,
          'image': 'https://image.eveonline.com/Type/2203_64.png', 'isk': 2283, 'special': None, 'size': 5},
    # Light 2
    105: {'id': 105, 'name': 'Warrior II', 'class': 10, 'attack': 1, 'defense': 0, 'maneuver': 3, 'tracking': 2,
          'image': 'https://image.eveonline.com/Type/2488_64.png', 'isk': 407854, 'special': None, 'size': 5},
    106: {'id': 106, 'name': 'Hobgoblin II', 'class': 10, 'attack': 3, 'defense': 0, 'maneuver': 1, 'tracking': 1,
          'image': 'https://image.eveonline.com/Type/2456_64.png', 'isk': 381735, 'special': None, 'size': 5},
    107: {'id': 107, 'name': 'Hornet II', 'class': 10, 'attack': 1.5, 'defense': 0, 'maneuver': 2, 'tracking': 1,
          'image': 'https://image.eveonline.com/Type/2466_64.png', 'isk': 464348, 'special': None, 'size': 5},
    108: {'id': 108, 'name': 'Acolyte II', 'class': 10, 'attack': 1.5, 'defense': 0, 'maneuver': 2, 'tracking': 1,
          'image': 'https://image.eveonline.com/Type/2205_64.png', 'isk': 448662, 'special': None, 'size': 5},
    # Medium
    109: {'id': 109, 'name': 'Valkyrie I', 'class': 11, 'attack': 1.5, 'defense': 0, 'maneuver': 1.5, 'tracking': 0,
          'image': 'https://image.eveonline.com/Type/15510_64.png', 'isk': 26169, 'special': None, 'size': 10},
    110: {'id': 110, 'name': 'Hammerhead I', 'class': 11, 'attack': 3.5, 'defense': 0, 'maneuver': 1, 'tracking': 0,
          'image': 'https://image.eveonline.com/Type/2183_64.png', 'isk': 16200, 'special': None, 'size': 10},
    111: {'id': 111, 'name': 'Vespa I', 'class': 11, 'attack': 1.75, 'defense': 0, 'maneuver': 1, 'tracking': 0,
          'image': 'https://image.eveonline.com/Type/15508_64.png', 'isk': 31000, 'special': None, 'size': 10},
    112: {'id': 112, 'name': 'Infiltrator I', 'class': 11, 'attack': 1.75, 'defense': 0, 'maneuver': 1, 'tracking': 0,
          'image': 'https://image.eveonline.com/Type/2173_64.png', 'isk': 9022, 'special': None, 'size': 10},
    # Medium 2
    113: {'id': 113, 'name': 'Valkyrie II', 'class': 11, 'attack': 2, 'defense': 0, 'maneuver': 2, 'tracking': 1,
          'image': 'https://image.eveonline.com/Type/21640_64.png', 'isk': 826070, 'special': None, 'size': 10},
    114: {'id': 114, 'name': 'Hammerhead II', 'class': 11, 'attack': 4.5, 'defense': 0, 'maneuver': 1, 'tracking': 0,
          'image': 'https://image.eveonline.com/Type/2185_64.png', 'isk': 840000, 'special': None, 'size': 10},
    115: {'id': 115, 'name': 'Vespa II', 'class': 11, 'attack': 2.25, 'defense': 0, 'maneuver': 2, 'tracking': 0,
          'image': 'https://image.eveonline.com/Type/221638_64.png', 'isk': 1300011, 'special': None, 'size': 10},
    116: {'id': 116, 'name': 'Infiltrator II', 'class': 11, 'attack': 2.25, 'defense': 0, 'maneuver': 2, 'tracking': 0,
          'image': 'https://image.eveonline.com/Type/2175_64.png', 'isk': 824013, 'special': None, 'size': 10},
    # Mining
    121: {'id': 121, 'name': 'Mining Drone I', 'class': 14, 'attack': 0, 'defense': 0, 'maneuver': 0, 'tracking': 0,
          'image': 'https://image.eveonline.com/Type/10246_64.png', 'isk': 18316, 'special': '5% Mining Bonus',
          'size': 5},
    122: {'id': 122, 'name': 'Mining Drone II', 'class': 14, 'attack': 0, 'defense': 0, 'maneuver': 0, 'tracking': 0,
          'image': 'https://image.eveonline.com/Type/10250_64.png', 'isk': 831869, 'special': '10% Mining Bonus',
          'size': 5},
    # PVE Loot
    200: {'id': 200, 'name': 'Republic Fleet Shield Extender', 'class': 2, 'attack': 0, 'defense': 0.35, 'maneuver': 0,
          'tracking': 0,
          'image': 'https://image.eveonline.com/Type/31928_64.png', 'isk': 7558297, 'special': None},
    201: {'id': 201, 'name': 'Shadow Serpentis Afterburner', 'class': 3, 'attack': 0, 'defense': 0, 'maneuver': 0.4,
          'tracking': 0,
          'image': 'https://image.eveonline.com/Type/14108_64.png', 'isk': 20633947, 'special': None},
    202: {'id': 202, 'name': "Imperial Navy Reinforced Steel Plates", 'class': 2, 'attack': 0, 'defense': 0.45,
          'maneuver': -0.1, 'tracking': 0,
          'image': 'https://image.eveonline.com/Type/31916_64.png', 'isk': 11134431, 'special': None},
    203: {'id': 203, 'name': 'Republic Fleet Microwarpdrive', 'class': 3, 'attack': 0, 'defense': 0, 'maneuver': 0.5,
          'tracking': -.15,
          'image': 'https://image.eveonline.com/Type/15747_64.png', 'isk': 27462971, 'special': None},
    204: {'id': 204, 'name': 'Republic Fleet Gyrostabilizer', 'class': 1, 'attack': .30, 'defense': 0, 'maneuver': 0,
          'tracking': .20,
          'image': 'https://image.eveonline.com/Type/15806_64.png', 'isk': 26722971, 'special': None},
    205: {'id': 205, 'name': "3rd Tier Overseer's Personal Effects", 'class': 20, 'attack': 0, 'defense': 0,
          'maneuver': 0,
          'tracking': 0,
          'image': 'https://image.eveonline.com/Type/19406_64.png', 'isk': 20001, 'special': None, 'no_fit': True},
    206: {'id': 206, 'name': "5th Tier Overseer's Personal Effects", 'class': 20, 'attack': 0, 'defense': 0,
          'maneuver': 0,
          'tracking': 0,
          'image': 'https://image.eveonline.com/Type/19406_64.png', 'isk': 65163, 'special': None, 'no_fit': True},
    207: {'id': 207, 'name': "7th Tier Overseer's Personal Effects", 'class': 20, 'attack': 0, 'defense': 0,
          'maneuver': 0,
          'tracking': 0,
          'image': 'https://image.eveonline.com/Type/19406_64.png', 'isk': 484113, 'special': None, 'no_fit': True},
    208: {'id': 208, 'name': "8th Tier Overseer's Personal Effects", 'class': 20, 'attack': 0, 'defense': 0,
          'maneuver': 0,
          'tracking': 0,
          'image': 'https://image.eveonline.com/Type/19406_64.png', 'isk': 700515, 'special': None, 'no_fit': True},
    500: {'id': 500, 'name': "tEVE PLEX", 'class': 20, 'attack': 0, 'defense': 0,
          'maneuver': 0,
          'tracking': 0,
          'image': 'https://image.eveonline.com/Type/44992_64.png', 'isk': 250000, 'special': None, 'no_fit': True},
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

mission_restrictions = {1: [0, 1, 2, 3, 4, 5, 6], 2: [1, 2, 3, 4, 5, 6], 3: [3, 4, 5, 6], 4: [5, 6], 5: [6]}

missions = {
    1: {'id': 1, 'name': 'Investigate The Transmission', 'level': 1,
        'initial': "While performing some maintenance on a communications relay, one of our techs noticed the logs "
                   "were showing a strange transmission coming from a deadspace pocket in this particular system. "
                   "We'd like you to travel to the system and figure out who or what sent out these transmissions.",
        'completion': "Interesting, well we look forward to working with you again in the future.",
        'special': None},
    2: {'id': 2, 'name': 'Put Down The Rebellion 1', 'level': 1,
        'initial': "Local security forces request your assistance. We have a small group of ships that need to be "
                   "dealt as soon as possible. These ships are members of the Serpentis faction and will put up a "
                   "fight.", 'completion': "Thanks for taking care of those guys, here's some ISK and you can keep "
                                           "any loot you might have found.",
        'special': None},
    3: {'id': 3, 'name': 'Put Down The Rebellion 2', 'level': 2,
        'initial': "Local security forces request your assistance. We have a small group of ships that need to be "
                   "dealt as soon as possible. These ships are members of the Serpentis faction and will put up a "
                   "fight.", 'completion': "Thanks for taking care of those guys, here's some ISK and you can keep "
                                           "any loot you might have found.",
        'special': None},
    4: {'id': 4, 'name': 'Put Down The Rebellion 3', 'level': 3,
        'initial': "Local security forces request your assistance. We have a small group of ships that need to be "
                   "dealt as soon as possible. These ships are members of the Serpentis faction and will put up a "
                   "fight.", 'completion': "Thanks for taking care of those guys, here's some ISK and you can keep "
                                           "any loot you might have found.",
        'special': None},
    5: {'id': 5, 'name': 'Put Down The Rebellion 4', 'level': 4,
        'initial': "Local security forces request your assistance. We have a small group of ships that need to be "
                   "dealt as soon as possible. These ships are members of the Serpentis faction and will put up a "
                   "fight.", 'completion': "Thanks for taking care of those guys, here's some ISK and you can keep "
                                           "any loot you might have found.",
        'special': None},
    6: {'id': 6, 'name': 'Put Down The Rebellion 5', 'level': 5,
        'initial': "Local security forces request your assistance. We have a small group of ships that need to be "
                   "dealt as soon as possible. These ships are members of the Serpentis faction and will put up a "
                   "fight.", 'completion': "Thanks for taking care of those guys, here's some ISK and you can keep "
                                           "any loot you might have found.",
        'special': None},
    7: {'id': 7, 'name': 'Illegal Drugs', 'level': 1,
        'initial': "Greetings Capsuleer.  A small convoy of freighters, that is transporting illegal drugs, has been sighted near you location. Your goal is to confront them and get the drugs, may it be peacefully or with force. They might have security so be careful, but be fast or the freighters are gone. The NDC will reward you for your help.",
        'completion': "Thank you for securing the drugs they will be safe with us. sniff We hope you will work with us again.",
        'special': None},
    12: {'id': 12, 'name': 'Illegal Drugs', 'level': 2,
         'initial': "Greetings Capsuleer.  A small convoy of freighters, that is transporting illegal drugs, has been sighted near you location. Your goal is to confront them and get the drugs, may it be peacefully or with force. They might have security so be careful, but be fast or the freighters are gone. The NDC will reward you for your help.",
         'completion': "Thank you for securing the drugs they will be safe with us. sniff We hope you will work with us again.",
         'special': None},
    8: {'id': 8, 'name': 'Drug Lord', 'level': 3,
        'initial': "Greetings Capsuleer. After inspecting the wreck of a freighter carrying lots of illegal drugs we found a booklet where the name Tenya Onoki was noted as being the person that sold them the drugs. We could track down this person. Though we could only narrow it down to the constellation, so you need to find and capture him. He will have a personal guard so be careful. The NDC wishes you the best of luck.",
        'completion': "Thank you for finding Tenya Onoki. We will interrogate him and hope to find the location of his production site. The NDC hopes to work with you again.",
        'special': None},
    11: {'id': 11, 'name': 'Drug Lord', 'level': 4,
         'initial': "Greetings Capsuleer. After inspecting the wreck of a freighter carrying lots of illegal drugs we found a booklet where the name Tenya Onoki was noted as being the person that sold them the drugs. We could track down this person. Though we could only narrow it down to the constellation, so you need to find and capture him. He will have a personal guard so be careful. The NDC wishes you the best of luck.",
         'completion': "Thank you for finding Tenya Onoki. We will interrogate him and hope to find the location of his production site. The NDC hopes to work with you again.",
         'special': None},
    9: {'id': 9, 'name': 'Drug Production Site', 'level': 3,
        'initial': "Greetings Capsuleer. After many days of interrogation we finally managed to find the place of his Production Site. We need to destroy it fast. However we don’t have the capabilities to do this, so we are asking you to help us once again. The NDC will be very happy if you could destroy the Site and its defenders and thus stop Onoki Medicals of producing any more illegal substances.",
        'completion': "Finally Onoki Medicals has been eliminated. Thank you for helping the NDC save many lives from drug addictions. We hope we will meet again.",
        'special': None},
    10: {'id': 10, 'name': 'Dimensional Horror', 'level': 5,
         'initial': "Alert!!! Capsuleers please listen. 10 years ago this region was nearly destroyed due to a Wormhole Anomaly never seen before. This Anomaly created a huge Monster named the Dimensional Horror. It can shoot a laser beam out of its mouth. Furthermore it screams silently, which damages your brain. Luckily it was destroyed, or so we thought, by the combined forces or the Amarr, Caldari, Minmitar and the Gallente. However it appeared again today. The 4 Empires have agreed that this is top priority. Every Capsuleer should come to fight the Dimensional Horror. For the future of New Eden.",
         'completion': "There is no way we can thank you enough Capsuleer. Take this small Reward for killing the Dimensional Horror once again and let’s hope it’s the last time.",
         'special': None},
    13: {'id': 13, 'name': 'Drug Production Site', 'level': 4,
         'initial': "Greetings Capsuleer. After many days of interrogation we finally managed to find the place of his Production Site. We need to destroy it fast. However we don’t have the capabilities to do this, so we are asking you to help us once again. The NDC will be very happy if you could destroy the Site and its defenders and thus stop Onoki Medicals of producing any more illegal substances.",
         'completion': "Finally Onoki Medicals has been eliminated. Thank you for helping the NDC save many lives from drug addictions. We hope we will meet again.",
         'special': None},
    14: {'id': 14, 'name': 'Drug Production Site', 'level': 2,
         'initial': "Greetings Capsuleer. After many days of interrogation we finally managed to find the place of his Production Site. We need to destroy it fast. However we don’t have the capabilities to do this, so we are asking you to help us once again. The NDC will be very happy if you could destroy the Site and its defenders and thus stop Onoki Medicals of producing any more illegal substances.",
         'completion': "Finally Onoki Medicals has been eliminated. Thank you for helping the NDC save many lives from drug addictions. We hope we will meet again.",
         'special': None},
}

npc = {
    1: {'id': 1, 'name': 'Centii Fugitive', 'class': 0, 'hit_points': 2, 'attack': 1, 'defense': 1, 'maneuver': 2,
        'tracking': 15,
        'image': 'http://games.chruker.dk/eve_online/graphics/ids/64/1238.jpg', 'isk': 3000},
    2: {'id': 2, 'name': 'Centior Cannibal', 'class': 0, 'hit_points': 3, 'attack': 2, 'defense': 2, 'maneuver': 2,
        'tracking': 13, 'image': 'http://games.chruker.dk/eve_online/graphics/ids/64/1237.jpg', 'isk': 11813},
    3: {'id': 3, 'name': 'Centum Ravisher', 'class': 0, 'hit_points': 4, 'attack': 3, 'defense': 2, 'maneuver': 2,
        'tracking': 8,
        'image': 'http://games.chruker.dk/eve_online/graphics/ids/64/1236.jpg', 'isk': 37500},
    4: {'id': 4, 'name': 'True Centii Enslaver', 'class': 1, 'hit_points': 2, 'attack': 3, 'defense': 1, 'maneuver': 5,
        'tracking': 15, 'image': 'http://games.chruker.dk/eve_online/graphics/ids/64/1237.jpg', 'isk': 8625},
    5: {'id': 5, 'name': 'Centior Horror', 'class': 1, 'hit_points': 4, 'attack': 5, 'defense': 6, 'maneuver': 4,
        'tracking': 8, 'image': 'http://games.chruker.dk/eve_online/graphics/ids/64/1237.jpg', 'isk': 15750},
    6: {'id': 6, 'name': 'Renegade Sanshas Slaver', 'class': 1, 'hit_points': 7, 'attack': 8, 'defense': 5, 'maneuver': 3,
        'tracking': 8, 'image': 'http://games.chruker.dk/eve_online/graphics/ids/64/1236.jpg', 'isk': 75000},
    7: {'id': 7, 'name': 'Centatis Specter', 'class': 1, 'hit_points': 8, 'attack': 9, 'defense': 6, 'maneuver': 2,
        'tracking': 7, 'image': 'https://image.eveonline.com/Type/606_64.png', 'isk': 135000},
    8: {'id': 8, 'name': "Sansha's Berserker", 'class': 2, 'hit_points': 3, 'attack': 5, 'defense': 3, 'maneuver': 5,
        'tracking': 15, 'image': 'http://games.chruker.dk/eve_online/graphics/ids/64/1237.jpg', 'isk': 12500},
    9: {'id': 9, 'name': 'True Centum Fiend', 'class': 2, 'hit_points': 6, 'attack': 12, 'defense': 8, 'maneuver': 3,
        'tracking': 11, 'image': 'http://games.chruker.dk/eve_online/graphics/ids/64/1237.jpg', 'isk': 88150},
    10: {'id': 10, 'name': 'Centus Dread Lord', 'class': 2, 'hit_points': 14, 'attack': 15, 'defense': 12, 'maneuver': 2,
         'tracking': 3, 'image': 'http://games.chruker.dk/eve_online/graphics/ids/64/2295.jpg', 'isk': 1162500},
    11: {'id': 11, 'name': 'True Centus Tyrant', 'class': 2, 'hit_points': 17, 'attack': 17, 'defense': 15, 'maneuver': 1,
         'tracking': 2, 'image': 'http://games.chruker.dk/eve_online/graphics/ids/64/2295.jpg', 'isk': 1443750},
    12: {'id': 12, 'name': 'Athran Agent', 'class': 10, 'hit_points': 2, 'attack': 2, 'defense': 1, 'maneuver': 2,
         'tracking': 16, 'image': 'http://games.chruker.dk/eve_online/graphics/ids/64/1858.jpg', 'isk': 3000},
    13: {'id': 13, 'name': "Khanid Wingman", 'class': 11, 'hit_points': 3, 'attack': 3, 'defense': 2, 'maneuver': 5,
         'tracking': 13, 'image': 'http://games.chruker.dk/eve_online/graphics/ids/64/1860.jpg', 'isk': 15750},
    14: {'id': 14, 'name': 'Khanid Eagle', 'class': 12, 'hit_points': 5, 'attack': 7, 'defense': 6, 'maneuver': 3,
         'tracking': 9, 'image': 'http://games.chruker.dk/eve_online/graphics/ids/64/1857.jpg', 'isk': 75000},
    15: {'id': 15, 'name': 'Khanid Warbird', 'class': 13, 'hit_points': 8, 'attack': 12, 'defense': 8, 'maneuver': 2,
         'tracking': 7, 'image': 'http://games.chruker.dk/eve_online/graphics/ids/64/1856.jpg', 'isk': 1162500},
    16: {'id': 16, 'name': 'Khanid High Commander', 'class': 14, 'hit_points': 17, 'attack': 17, 'defense': 15, 'maneuver': 1,
         'tracking': 2, 'image': 'http://games.chruker.dk/eve_online/graphics/ids/64/20333.jpg', 'isk': 1443750},
}
