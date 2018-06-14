import sqlite3


async def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    c = conn.cursor()
    c.execute(create_table_sql)


async def create_tables():
    db = sqlite3.connect('aura.sqlite')
    if db is not None:
        # create general table
        aura_table = """ CREATE TABLE IF NOT EXISTS aura (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        entry TEXT NOT NULL UNIQUE,
                                        value TEXT NOT NULL,
                                        additional_value TEXT DEFAULT NULL
                                    ); """
        await create_table(db, aura_table)
        # create general table
        data_table = """ CREATE TABLE IF NOT EXISTS data (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        entry TEXT NOT NULL UNIQUE,
                                        int INTEGER DEFAULT 0,
                                        text TEXT DEFAULT NULL
                                    ); """
        await create_table(db, data_table)
        # create whitelist table
        whitelist_table = """ CREATE TABLE IF NOT EXISTS whitelist (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        location_id INTEGER,
                                        role_id INTEGER NOT NULL
                                    ); """
        await create_table(db, whitelist_table)
        # create fleets tables
        fleets_table = """ CREATE TABLE IF NOT EXISTS fleet_info (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        fleet_id INTEGER NOT NULL UNIQUE,
                                        fleet_fc INTEGER NOT NULL,
                                        fleet_members INTEGER NOT NULL,
                                        access INTEGER DEFAULT 2
                                    ); """
        await create_table(db, fleets_table)
        # create regions tables
        regions_table = """ CREATE TABLE IF NOT EXISTS region_info (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        region_id INTEGER NOT NULL UNIQUE,
                                        region_security TEXT NOT NULL,
                                        mineral INTEGER DEFAULT NULL,
                                        pirate_anomaly INTEGER DEFAULT 0,
                                        mining_anomaly INTEGER DEFAULT 0,
                                        incursion INTEGER DEFAULT 0,
                                        npc_kills_hour INTEGER DEFAULT 0,
                                        npc_kills_day INTEGER DEFAULT 0,
                                        player_kills_hour INTEGER DEFAULT 0,
                                        player_kills_day INTEGER DEFAULT 0,
                                        npc_kills_previous_hour INTEGER DEFAULT 0,
                                        npc_kills_previous_day INTEGER DEFAULT 0,
                                        player_kills_previous_hour INTEGER DEFAULT 0,
                                        player_kills_previous_day INTEGER DEFAULT 0
                                    ); """
        await create_table(db, regions_table)
        # create regions tables
        region_market_table = """ CREATE TABLE IF NOT EXISTS region_market (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        region_id INTEGER NOT NULL UNIQUE,
                                        owner_id INTEGER DEFAULT NULL,
                                        type INTEGER DEFAULT NULL,
                                        ship INTEGER DEFAULT NULL,
                                        module INTEGER DEFAULT NULL,
                                        component INTEGER DEFAULT NULL,
                                        quantity INTEGER DEFAULT NULL,
                                        price INTEGER DEFAULT NULL
                                    ); """
        await create_table(db, region_market_table)
        # create corps tables
        corps_table = """ CREATE TABLE IF NOT EXISTS corporations (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        corp_id INTEGER DEFAULT NULL,
                                        alliance INTEGER DEFAULT NULL,
                                        name TEXT DEFAULT NULL,
                                        ticker TEXT DEFAULT NULL UNIQUE,
                                        ceo INTEGER NOT NULL,
                                        officers TEXT DEFAULT NULL,
                                        members TEXT DEFAULT NULL,
                                        pending_members TEXT DEFAULT NULL,
                                        corp_offices TEXT DEFAULT NULL,
                                        corp_ship_hangar TEXT DEFAULT NULL,
                                        corp_module_hangar TEXT DEFAULT NULL,
                                        wallet INTEGER DEFAULT 0,
                                        tax_rate INTEGER DEFAULT 0
                                    ); """
        await create_table(db, corps_table)
        # create eve_rpg tables
        eve_rpg_channels_table = """ CREATE TABLE IF NOT EXISTS eve_rpg_channels (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        server_id INTEGER NOT NULL UNIQUE,
                                        channel_id STRING NOT NULL,
                                        owner_id INTEGER NOT NULL
                                    ); """
        await create_table(db, eve_rpg_channels_table)
        eve_rpg_players_table = """ CREATE TABLE IF NOT EXISTS eve_rpg_players (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        server_id INTEGER NOT NULL,
                                        player_id INTEGER NOT NULL UNIQUE,
                                        race INTEGER DEFAULT 0,
                                        region INTEGER DEFAULT 0,
                                        isk INTEGER DEFAULT 0,
                                        task INTEGER DEFAULT 1,
                                        last_event TEXT DEFAULT NULL,
                                        level INTEGER DEFAULT 0,
                                        xp INTEGER DEFAULT 0,
                                        kills INTEGER DEFAULT 0,
                                        losses INTEGER DEFAULT 0,
                                        modules TEXT DEFAULT NULL,
                                        module_hangar TEXT DEFAULT NULL,
                                        ship TEXT DEFAULT 0,
                                        ship_hangar TEXT DEFAULT NULL,
                                        fleet INTEGER DEFAULT 0,
                                        destination INTEGER DEFAULT 0,
                                        home INTEGER DEFAULT 1,
                                        component_hangar TEXT DEFAULT NULL,
                                        wallet_journal TEXT DEFAULT NULL,
                                        blue_players TEXT DEFAULT NULL,
                                        mission_details TEXT DEFAULT NULL,
                                        corporation INTEGER DEFAULT NULL,
                                        alliance INTEGER DEFAULT NULL,
                                        combat_timer INTEGER DEFAULT NULL,
                                        saved_fits TEXT DEFAULT NULL
                                    ); """
        await create_table(db, eve_rpg_players_table)
    else:
        print('Database: Unable to connect to the database')


async def update_tables():
    db = sqlite3.connect('aura.sqlite')
    sql = ''' SELECT int FROM data WHERE `entry` = 'db_version' '''
    version = await select(sql)
    if len(version) == 0:
        current_version = 0
    else:
        current_version = version[0][0]
    if db is not None:
        result = 'DB Up To Date'
        if int(current_version) < 6:
            result = 'Updated to DB version 6'
            sql = ''' ALTER TABLE region_info ADD COLUMN `npc_kills_previous_hour` INTEGER DEFAULT 0; '''
            await execute_sql(sql)
            sql = ''' ALTER TABLE region_info ADD COLUMN `npc_kills_previous_day` INTEGER DEFAULT 0; '''
            await execute_sql(sql)
            sql = ''' ALTER TABLE region_info ADD COLUMN `player_kills_previous_hour` INTEGER DEFAULT 0; '''
            await execute_sql(sql)
            sql = ''' ALTER TABLE region_info ADD COLUMN `player_kills_previous_day` INTEGER DEFAULT 0; '''
            await execute_sql(sql)
        sql = ''' REPLACE INTO data(entry,int)
                  VALUES(?,?) '''
        values = ('db_version', 6)
        await execute_sql(sql, values)
        return result


async def select(sql, single=False):
    db = sqlite3.connect('aura.sqlite')
    cursor = db.cursor()
    cursor.execute(sql)
    try:
        if single:
            data = cursor.fetchone()[0]
        else:
            data = cursor.fetchall()
    except:
        data = None
    db.close()
    return data


async def select_var(sql, var, single=False):
    db = sqlite3.connect('aura.sqlite')
    cursor = db.cursor()
    cursor.execute(sql, var)
    try:
        if single:
            data = cursor.fetchone()[0]
        else:
            data = cursor.fetchall()
    except:
        data = None
    db.close()
    return data


async def get_token(sql, single=False):
    db = sqlite3.connect('aura.sqlite')
    cursor = db.cursor()
    cursor.execute(sql)
    try:
        if single:
            data = cursor.fetchone()[0]
        else:
            data = cursor.fetchall()
    except:
        data = None
    db.close()
    return data


async def execute_sql(sql, var=None):
    db = sqlite3.connect('aura.sqlite')
    cursor = db.cursor()
    if var is not None:
        cursor.execute(sql, var)
    else:
        cursor.execute(sql)
    db.commit()
    db.close()
