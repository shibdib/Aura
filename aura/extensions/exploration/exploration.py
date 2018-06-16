import random
import datetime
import ast

from discord.ext import commands

from aura.core import checks
from aura.lib import db
from aura.lib import game_functions
from aura.utils import make_embed


async def update_journal(player, isk, entry):
    player = await game_functions.refresh_player(player)
    utc = datetime.datetime.utcnow()
    time = utc.strftime("%H:%M:%S")
    if player[20] is not None:
        journal = ast.literal_eval(player[20])
        if len(journal) == 10:
            journal.pop(0)
        transaction = {'isk': isk, 'type': entry, 'time': time}
        journal.append(transaction)
    else:
        transaction = {'isk': isk, 'type': entry, 'time': time}
        journal = [transaction]
    sql = ''' UPDATE eve_rpg_players
            SET wallet_journal = (?)
            WHERE
                player_id = (?); '''
    values = (str(journal), player[2],)
    return await db.execute_sql(sql, values)


async def weighted_choice(items):
    """items is a list of tuples in the form (item, weight)"""
    weight_total = sum((item[1] for item in items))
    n = random.uniform(0, weight_total)
    for item, weight in items:
        if n < weight:
            return item
        n = n - weight
    return item


async def add_isk(player, isk):
    player = await game_functions.refresh_player(player)
    sql = ''' UPDATE eve_rpg_players
            SET isk = (?)
            WHERE
                player_id = (?); '''
    values = (int(player[5]) + isk, player[2],)
    return await db.execute_sql(sql, values)


async def add_xp(player, xp_gained):
    player = await game_functions.refresh_player(player)
    if player[9] + xp_gained < 100 * player[8]:
        sql = ''' UPDATE eve_rpg_players
                SET xp = (?)
                WHERE
                    player_id = (?); '''
        values = (player[9] + xp_gained, player[2],)
    else:
        sql = ''' UPDATE eve_rpg_players
                SET level = (?),
                    xp = (?)
                WHERE
                    player_id = (?); '''
        values = (player[8] + 1, 0, player[2],)
    return await db.execute_sql(sql, values)


class Exploration:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session
        self.config = bot.config
        self.logger = bot.logger

    @commands.command(name='explore', case_insensitive=True)
    @checks.spam_check()
    @checks.is_whitelist()
    @checks.has_account()
    async def explore(self, ctx):
        """Run a site."""
        if ctx.guild is not None:
            try:
                await ctx.message.delete()
            except Exception:
                pass
        sql = ''' SELECT * FROM eve_rpg_players WHERE `player_id` = (?) '''
        values = (ctx.message.author.id,)
        player = await db.select_var(sql, values)
        if player[0][6] is 1:
            await ctx.author.send('**ERROR** - You must be undocked to do this.')
            return await ctx.invoke(self.bot.get_command("me"), True)
        explorer = player[0]
        region_id = int(explorer[4])
        region_security = await game_functions.get_region_security(region_id)
        isk = random.randint(3000, 7500)
        best_of = 3
        loot_chance = 2
        if region_security == 'Low':
            isk = random.randint(6500, 12500)
            best_of = 5
            loot_chance = 4
        elif region_security == 'Null':
            isk = random.randint(10500, 20500)
            best_of = 5
            loot_chance = 7
        #  PVE Rolls
        find_sites = await weighted_choice([(True, 60), (False, 40)])
        if find_sites is False:
            await ctx.author.send('**No Sites Found** - Failed to find any sites, try again.')
            return await ctx.invoke(self.bot.get_command("task"), True)
        else:
            player = self.bot.get_user(explorer[2])
            embed = make_embed(icon=self.bot.user.avatar)
            embed.set_footer(icon_url=self.bot.user.avatar_url,
                             text="Aura - EVE Text RPG")
            embed.add_field(name="Site Found",
                            value="You've located an empty site and begin trying to hack the storage containers in "
                                  "the area.")
            await player.send(embed=embed)
            your_score = 0
            ai_score = 0
            last_action = ''
            win = False
            for x in range(11):
                if your_score >= best_of:
                    win = True
                    break
                if ai_score >= best_of:
                    win = False
                    break
                embed = make_embed(icon=self.bot.user.avatar)
                embed.set_footer(icon_url=self.bot.user.avatar_url,
                                 text="Aura - EVE Text RPG")
                embed.add_field(name="Hacking",
                                value="Someone is countering your hack...\n\n"
                                      "{}"
                                      "Your Hack Score: {}\n"
                                      "Hostile Hack Score: {}\n\n"
                                      "__Choose an action__\n"
                                      "**B.** Brute Attack\n"
                                      "**F.** Firewall\n"
                                      "**T.** Trojan Attack\n".format(last_action, your_score, ai_score))
                await player.send(embed=embed)

                def check(m):
                    return m.author == player and m.channel == player.dm_channel

                msg = await self.bot.wait_for('message', check=check, timeout=120.0)
                response = msg.content.lower()
                if response != 'b' and response != 'f' and response != 't':
                    last_action = '**Last Action:** Incorrect Response\n'
                    ai_score += 1
                    continue
                ai_action = await weighted_choice([('1', 33), ('2', 33), ('3', 33)])
                if response == 'b' and ai_action != '2' and ai_action != response:
                    last_action = '**Last Action:** Brute Attack Successful\n'
                    your_score += 1
                    continue
                if response == 'b' and ai_action == '2':
                    last_action = '**Last Action:** Brute Attack Stopped By Firewall\n'
                    ai_score += 1
                    continue
                if response == 'f' and ai_action != '3' and ai_action != response:
                    last_action = '**Last Action:** Firewall Successful\n'
                    your_score += 1
                    continue
                if response == 'f' and ai_action == '3':
                    last_action = '**Last Action:** Trojan Attack Countered Your Firewall\n'
                    ai_score += 1
                    continue
                if response == 't' and ai_action != '1' and ai_action != response:
                    last_action = '**Last Action:** Trojan Attack Successful\n'
                    your_score += 1
                    continue
                if response == 't' and ai_action == '1':
                    last_action = '**Last Action:** Brute Attack Overwhelmed Your Trojan Attack Attempt\n'
                    ai_score += 1
                    continue
            if win is True:
                xp_gained = await weighted_choice([(2, 35), (3, 15), (0, 15)])
                await add_xp(explorer, xp_gained)
                await add_isk(explorer, isk)
                await update_journal(explorer, isk, 'Exploration')
                await player.send(
                    '**Success** Site succesfully hacked for {} ISK, hunting for a new site.'.format(isk))
                await self.pve_loot(explorer, loot_chance)
            else:
                await player.send('**Failure** The AI defeated you, looking for a new site.')

    async def pve_loot(self, player, chance, overseer=False, officer=False):
        false = 200 - int(chance)
        loot_drop = await weighted_choice([(True, chance), (False, false)])
        if loot_drop is True or officer is True:
            player = await game_functions.refresh_player(player)
            ship = ast.literal_eval(player[14])
            loot_type = await weighted_choice([(200, 25), (201, 25), (202, 25), (203, 25), (204, 25)])
            item = await game_functions.get_module(loot_type)
            if 'module_cargo_bay' in ship:
                loot = ship['module_cargo_bay']
                loot.append(loot_type)
            else:
                loot = [loot_type]
            channel = self.bot.get_user(player[2])
            await channel.send('**PVE Loot Received**\n\n**{}**\n\n*Get to a station and empty your module '
                               'bay to get it*'.format(item['name']))
            ship['module_cargo_bay'] = loot
            sql = ''' UPDATE eve_rpg_players
                    SET ship = (?)
                    WHERE
                        player_id = (?); '''
            values = (str(ship), player[2],)
            await db.execute_sql(sql, values)
        if overseer is True:
            player = await game_functions.refresh_player(player)
            ship = ast.literal_eval(player[14])
            loot_type = await weighted_choice([(205, 50), (206, 25), (207, 10), (208, 5)])
            item = await game_functions.get_module(loot_type)
            if 'module_cargo_bay' in ship:
                loot = ship['module_cargo_bay']
                loot.append(loot_type)
            else:
                loot = [loot_type]
            channel = self.bot.get_user(player[2])
            await channel.send('**PVE Loot Received**\n\n**{}**\n\n*Get to a station and empty your module '
                               'bay to get it*'.format(item['name']))
            ship['module_cargo_bay'] = loot
            sql = ''' UPDATE eve_rpg_players
                    SET ship = (?)
                    WHERE
                        player_id = (?); '''
            values = (str(ship), player[2],)
            await db.execute_sql(sql, values)
