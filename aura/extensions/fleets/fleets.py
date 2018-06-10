import ast

from discord.ext import commands

from aura.core import checks
from aura.lib import db
from aura.lib import game_functions
from aura.utils import make_embed


class Fleets:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session
        self.config = bot.config
        self.logger = bot.logger

    @commands.command(name='fleet', case_insensitive=True)
    @checks.spam_check()
    @checks.is_whitelist()
    @checks.has_account()
    async def _fleets(self, ctx):
        """Fleet Menu."""
        if ctx.guild is not None:
            try:
                await ctx.message.delete()
            except Exception:
                pass
        if ctx.invoked_subcommand is None:
            sql = ''' SELECT * FROM eve_rpg_players WHERE `player_id` = (?) '''
            values = (ctx.message.author.id,)
            player = await db.select_var(sql, values)
            player_name = self.bot.get_user(int(player[0][2])).display_name
            if player[0][16] is not None and player[0][16] != 0:
                sql = ''' SELECT * FROM fleet_info WHERE `fleet_id` = (?) '''
                values = (player[0][16],)
                fleet_info = await db.select_var(sql, values)
                if fleet_info[0][2] == player[0][0]:
                    embed = make_embed(icon=ctx.bot.user.avatar)
                    embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                                     text="Aura - EVE Text RPG")
                    embed.add_field(name="Fleet Management".format(player_name),
                                    value="**1.** Disband Fleet\n"
                                          "**2.** Kick Member\n"
                                          "**3.** Return to the main menu")
                    await ctx.author.send(embed=embed)

                    def check(m):
                        return m.author == ctx.author and m.channel == ctx.author.dm_channel

                    msg = await self.bot.wait_for('message', check=check, timeout=120)
                    content = msg.content
                    if content == '1':
                        await self.disband_fleet(ctx, fleet_info[0])
                    elif content == '2':
                        await self.kick_member(ctx, fleet_info[0])
                    elif content == '3':
                        await ctx.invoke(self.bot.get_command("me"), True)
                    elif '!!' not in content:
                        await ctx.author.send('**ERROR** - Not a valid choice.')
                        if content.find('!!') == -1:
                            return await ctx.invoke(self.bot.get_command("me"), True)
                        else:
                            return
                else:
                    embed = make_embed(icon=ctx.bot.user.avatar)
                    embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                                     text="Aura - EVE Text RPG")
                    embed.add_field(name="Fleet Management".format(player_name),
                                    value="**1.** Leave Fleet\n"
                                          "**2.** Return to the main menu")
                    await ctx.author.send(embed=embed)

                    def check(m):
                        return m.author == ctx.author and m.channel == ctx.author.dm_channel

                    msg = await self.bot.wait_for('message', check=check, timeout=120)
                    content = msg.content
                    if content == '1':
                        await self.leave_fleet(ctx, player[0], fleet_info[0])
                    elif content == '2':
                        await ctx.invoke(self.bot.get_command("me"), True)
                    elif '!!' not in content:
                        await ctx.author.send('**ERROR** - Not a valid choice.')
                        if content.find('!!') == -1:
                            return await ctx.invoke(self.bot.get_command("me"), True)
                        else:
                            return
            else:
                embed = make_embed(icon=ctx.bot.user.avatar)
                embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                                 text="Aura - EVE Text RPG")
                embed.add_field(name="Fleet Management".format(player_name),
                                value="**1.** Create a Fleet\n"
                                      "**2.** Join a Fleet\n"
                                      "**3.** Return to the main menu")
                await ctx.author.send(embed=embed)

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.author.dm_channel

                msg = await self.bot.wait_for('message', check=check, timeout=120)
                content = msg.content
                if content == '1':
                    await self.create_fleet(ctx, player[0])
                elif content == '2':
                    await self.join_fleet(ctx, player[0])
                elif content == '3':
                    await ctx.invoke(self.bot.get_command("me"), True)
                elif '!!' not in content:
                    await ctx.author.send('**ERROR** - Not a valid choice.')
                    if content.find('!!') == -1:
                        return await ctx.invoke(self.bot.get_command("me"), True)
                    else:
                        return

    async def create_fleet(self, ctx, player):
        sql = ''' UPDATE eve_rpg_players
                    SET fleet = (?)
                    WHERE
                        player_id = (?); '''
        unique_id = await game_functions.create_unique_id()
        values = (unique_id, ctx.author.id,)
        await db.execute_sql(sql, values)
        sql = ''' REPLACE INTO fleet_info(fleet_id,fleet_fc,fleet_members)
                  VALUES(?,?,?) '''
        values = (unique_id, player[0], str([player[0]]))
        await db.execute_sql(sql, values)
        await ctx.author.send('**Success** - Fleet created.')
        await ctx.invoke(self.bot.get_command("me"), True)

    async def join_fleet(self, ctx, player):
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Join Fleet",
                        value="What is the player ID of the FC?\n\n"
                              "*Users can find their player ID on the top of their !!me menu*")
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120)
        content = msg.content
        sql = ''' SELECT * FROM fleet_info WHERE `fleet_fc` = (?) '''
        values = (int(content),)
        fleet = await db.select_var(sql, values)
        if len(fleet) == 0:
            await ctx.author.send('**ERROR** - No fleet found.')
            return await ctx.invoke(self.bot.get_command("me"), True)
        if fleet[0][4] == 1:
            members = ast.literal_eval(fleet[0][3])
            members.append(player[0])
            sql = ''' UPDATE eve_rpg_players
                        SET fleet = (?)
                        WHERE
                            player_id = (?); '''
            values = (fleet[0][1], ctx.author.id,)
            await db.execute_sql(sql, values)
            sql = ''' UPDATE fleet_info
                        SET fleet_members = (?)
                        WHERE
                            fleet_id = (?); '''
            values = (members, fleet[0][1])
            await db.execute_sql(sql, values)
            await ctx.author.send('**Success** - Fleet created.')
            return await ctx.invoke(self.bot.get_command("me"), True)
        if fleet[0][4] == 2:
            sql = ''' SELECT * FROM eve_rpg_players WHERE `id` = (?) '''
            values = (int(content),)
            fc = await db.select_var(sql, values)
            if fc[0][21] is not None:
                blue_array = ast.literal_eval(fc[0][21])
                if player[0] in blue_array:
                    members = ast.literal_eval(fleet[0][3])
                    members.append(player[0])
                    sql = ''' UPDATE eve_rpg_players
                                SET fleet = (?)
                                WHERE
                                    player_id = (?); '''
                    values = (fleet[0][1], ctx.author.id,)
                    await db.execute_sql(sql, values)
                    sql = ''' UPDATE fleet_info
                                SET fleet_members = (?)
                                WHERE
                                    fleet_id = (?); '''
                    values = (members, fleet[0][1])
                    await db.execute_sql(sql, values)
                    await ctx.author.send('**Success** - Joined Fleet.')
                    return await ctx.invoke(self.bot.get_command("me"), True)
            await ctx.author.send('**Failure** - FC has set the fleet to only accept blues.')
            return await ctx.invoke(self.bot.get_command("me"), True)

    async def leave_fleet(self, ctx, player, fleet):
        sql = ''' UPDATE eve_rpg_players
                    SET fleet = (?)
                    WHERE
                        id = (?); '''
        values = (None, player[0],)
        await db.execute_sql(sql, values)
        members = ast.literal_eval(fleet[3])
        members.remove(player[0])
        sql = ''' UPDATE fleet_info
                    SET fleet_members = (?)
                    WHERE
                        fleet_id = (?); '''
        values = (members, fleet[1])
        await db.execute_sql(sql, values)
        await ctx.author.send('**Success** - Left Fleet.')
        await ctx.invoke(self.bot.get_command("me"), True)

    async def disband_fleet(self, ctx, fleet):
        sql = ''' UPDATE eve_rpg_players
                    SET fleet = (?)
                    WHERE
                        fleet = (?); '''
        values = (None, fleet[1],)
        await db.execute_sql(sql, values)
        sql = ''' DELETE FROM 
                        `fleet_info`
                    WHERE
                        `fleet_fc` = (?) '''
        values = (int(fleet[2]),)
        await db.execute_sql(sql, values)
        await ctx.author.send('**Success** - Fleet disbanded.')
        await ctx.invoke(self.bot.get_command("me"), True)

    async def kick_member(self, ctx, fleet):
        fleet_member_dict = {}
        fleet_member_array = []
        member_number = 1
        for member_id in fleet[3]:
            sql = ''' SELECT * FROM eve_rpg_players WHERE `id` = (?) '''
            values = (int(member_id),)
            member = await db.select_var(sql, values)
            member_name = self.bot.get_user(int(member[0][2])).display_name
            fleet_member_dict[member_number] = member[0][0]
            fleet_member_array.append('**{}.** {}'.format(member_number, member_name))
        clean_members = '\n'.join(fleet_member_array)
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Kick Member",
                        value="{}".format(clean_members))
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120)
        content = msg.content
        if int(content) not in fleet_member_dict:
            await ctx.author.send('**ERROR** - Incorrect Selection.')
            return await ctx.invoke(self.bot.get_command("me"), True)
        sql = ''' UPDATE eve_rpg_players
                    SET fleet = (?)
                    WHERE
                        id = (?); '''
        values = (None, fleet_member_dict[int(content)],)
        await db.execute_sql(sql, values)
        await ctx.author.send('**Success** - Member Kicked.')
        await ctx.invoke(self.bot.get_command("me"), True)
