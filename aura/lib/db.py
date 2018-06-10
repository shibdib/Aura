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
                                        access INTEGER DEFAULT 2,
                                    ); """
        await create_table(db, fleets_table)
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
                                        mission_details TEXT DEFAULT NULL
                                    ); """
        await create_table(db, eve_rpg_players_table)
        # create killmail table
        killmail_table = """ CREATE TABLE IF NOT EXISTS killmails (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        loser_discord_id INTEGER NOT NULL,
                                        loser_game_id INTEGER NOT NULL,
                                        loser_ship TEXT DEFAULT NULL,
                                        loser_task INTEGER DEFAULT 1,
                                        loser_modules TEXT DEFAULT NULL,
                                        loser_corp INTEGER DEFAULT NULL,
                                        loser_alliance INTEGER DEFAULT NULL,
                                        killer_discord_id INTEGER DEFAULT NULL,
                                        killer_game_id INTEGER DEFAULT NULL,
                                        killer_ship TEXT DEFAULT DEFAULT NULL,
                                        killer_task INTEGER DEFAULT 1,
                                        killer_fleet TEXT DEFAULT NULL,
                                        killer_corp INTEGER DEFAULT NULL,
                                        killer_alliance INTEGER DEFAULT NULL,
                                        killer_npc INTEGER DEFAULT NULL,
                                        region INTEGER DEFAULT 0,
                                        entry TEXT NOT NULL UNIQUE,
                                        int INTEGER DEFAULT 0,
                                        text TEXT DEFAULT NULL
                                    ); """
        await create_table(db, killmail_table)
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
        if int(current_version) < 2:
            result = 'Updated to DB version 1'
            sql = ''' ALTER TABLE eve_rpg_players ADD COLUMN `mission_details` TEXT DEFAULT NULL; '''
            await execute_sql(sql)
        sql = ''' REPLACE INTO data(entry,int)
                  VALUES(?,?) '''
        values = ('db_version', 2)
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
