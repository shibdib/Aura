import ast

from discord.ext import commands

from aura.core import checks
from aura.lib import db
from aura.lib import game_functions
from aura.utils import make_embed


class Corps:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session
        self.config = bot.config
        self.logger = bot.logger

    @commands.group(name='corp', case_insensitive=True)
    @checks.spam_check()
    @checks.is_whitelist()
    @checks.has_account()
    async def _corps(self, ctx):
        """Corporation Menu."""
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
            if player[0][23] is not None:
                corp_info = await game_functions.get_user_corp(player[0][23])
                corp_officers = []
                if corp_info[6] is not None:
                    corp_officers = ast.literal_eval(corp_info[6])
                if corp_info is None:
                    sql = ''' UPDATE eve_rpg_players
                                SET corporation = (?)
                                WHERE
                                    player_id = (?); '''
                    values = (None, ctx.author.id,)
                    await db.execute_sql(sql, values)
                    return await ctx.invoke(self.bot.get_command("corp"))
                pending_members = []
                if corp_info[8] is not None:
                    pending_members = ast.literal_eval(corp_info[8])
                corp_members = ast.literal_eval(corp_info[7])
                if corp_info[5] == player[0][0]:
                    embed = make_embed(icon=ctx.bot.user.avatar)
                    embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                                     text="Aura - EVE Text RPG")
                    embed.add_field(name="Corporation Management".format(player_name),
                                    value="__**Corporation Info**__\n"
                                          "Corp ID: {}\n"
                                          "Member Count: {}\n\n"
                                          "**1.** Review Pending Members ({} Waiting)\n"
                                          "**2.** Kick Member\n"
                                          "**3.** Manage Officers\n"
                                          "**4.** Disband Corporation\n"
                                          "**5.** Return to the main menu".format(corp_info[1], len(corp_members), len(pending_members)))
                    await ctx.author.send(embed=embed)

                    def check(m):
                        return m.author == ctx.author and m.channel == ctx.author.dm_channel

                    msg = await self.bot.wait_for('message', check=check, timeout=120)
                    content = msg.content
                    if content == '1':
                        await self.review_pending(ctx, corp_info)
                    elif content == '2':
                        await self.kick_member(ctx, corp_info)
                    elif content == '3':
                        await self.manage_officers(ctx, corp_info)
                    elif content == '4':
                        await self.disband_corporation(ctx, corp_info)
                    elif content == '5':
                        await ctx.invoke(self.bot.get_command("me"), True)
                    elif '!!' not in content:
                        await ctx.author.send('**ERROR** - Not a valid choice.')
                    elif content.find('!!') == -1:
                        return await ctx.invoke(self.bot.get_command("me"), True)
                    else:
                        return
                elif player[0][0] in corp_officers:
                    embed = make_embed(icon=ctx.bot.user.avatar)
                    embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                                     text="Aura - EVE Text RPG")
                    embed.add_field(name="Corporation Management".format(player_name),
                                    value="__**Corporation Info**__\n"
                                          "Corp ID: {}\n"
                                          "Member Count: {}\n\n"
                                          "**1.** Review Pending Members ({} Waiting)\n"
                                          "**2.** Kick Member\n"
                                          "**3.** Return to the main menu".format(corp_info[1], len(corp_members), len(pending_members)))
                    await ctx.author.send(embed=embed)

                    def check(m):
                        return m.author == ctx.author and m.channel == ctx.author.dm_channel

                    msg = await self.bot.wait_for('message', check=check, timeout=120)
                    content = msg.content
                    if content == '1':
                        await self.review_pending(ctx, corp_info)
                    elif content == '2':
                        await self.kick_member(ctx, corp_info)
                    elif content == '3':
                        await ctx.invoke(self.bot.get_command("me"), True)
                    elif '!!' not in content:
                        await ctx.author.send('**ERROR** - Not a valid choice.')
                    elif content.find('!!') == -1:
                        return await ctx.invoke(self.bot.get_command("me"), True)
                    else:
                        return
                else:
                    await ctx.invoke(self.bot.get_command("me"), True)
            else:
                embed = make_embed(icon=ctx.bot.user.avatar)
                embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                                 text="Aura - EVE Text RPG")
                embed.add_field(name="Corporation Management".format(player_name),
                                value="**1.** Create a Corporation\n"
                                      "**2.** Join a Corporation\n"
                                      "**3.** Return to the main menu")
                await ctx.author.send(embed=embed)

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.author.dm_channel

                msg = await self.bot.wait_for('message', check=check, timeout=120)
                content = msg.content
                if content == '1':
                    await self.create_corp(ctx, player[0])
                elif content == '2':
                    await self.join_corp(ctx, player[0])
                elif content == '3':
                    await ctx.invoke(self.bot.get_command("me"), True)
                elif '!!' not in content:
                    await ctx.author.send('**ERROR** - Not a valid choice.')
                    if content.find('!!') == -1:
                        return await ctx.invoke(self.bot.get_command("me"), True)
                    else:
                        return

    async def create_corp(self, ctx, player):
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Create Corporation",
                        value="What do you want to name your corporation?\n\n"
                              "*Names should not exceed 15 characters.*\n\n"
                              "*Vulgar names will result in GM action.*\n\n"
                              "Type **!!me** to cancel this action.")
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120)
        if msg.content == '!!me':
            return await ctx.invoke(self.bot.get_command("me"), True)
        corp_name = msg.content[:15]
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Create Corporation",
                        value="What would you like your corp ticker to be?\n\n"
                              "*Tickers should not exceed 5 characters.*\n\n"
                              "*Vulgar tickers will result in GM action.*\n\n"
                              "Type **!!me** to cancel this action.")
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120)
        if msg.content == '!!me':
            return await ctx.invoke(self.bot.get_command("me"), True)
        ticker = msg.content[:15]
        sql = ''' SELECT * FROM corporations WHERE `ticker` = (?) '''
        values = (ticker,)
        tickers = await db.select_var(sql, values)
        if len(tickers) > 0:
            await ctx.author.send('**ERROR** - Ticker already taken.')
            return await ctx.invoke(self.bot.get_command("corp"), True)
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Create Corporation",
                        value="__**Confirmation**__\n"
                              "**CREATING A CORPORATION COSTS 50,000,000 ISK**\n\n"
                              "Corp Name: {}\n"
                              "Corp Ticker: [{}]\n\n"
                              "**1.** Confirm\n"
                              "**2.** Cancel\n\n"
                              "Type **!!me** to cancel this action.".format(corp_name, ticker))
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120)
        if msg.content == '!!me' or msg.content != '1':
            return await ctx.invoke(self.bot.get_command("me"), True)
        if int(50000000) > int(float(player[5])):
            await ctx.author.send('**Not Enough Isk**')
            return await ctx.invoke(self.bot.get_command("me"), True)
        sql = ''' UPDATE eve_rpg_players
                    SET corporation = (?),
                        isk = (?)
                    WHERE
                        player_id = (?); '''
        unique_id = await game_functions.create_unique_id()
        values = (unique_id, int(float(player[5])) - int(50000000), ctx.author.id,)
        await db.execute_sql(sql, values)
        sql = ''' REPLACE INTO corporations(corp_id,name,ticker,ceo,members,corp_offices)
                  VALUES(?,?,?,?,?,?) '''
        values = (unique_id, corp_name, ticker, player[0], str([player[0]]), str([player[4]]))
        await db.execute_sql(sql, values)
        await ctx.author.send('**Success** - Corporation created.')
        await ctx.invoke(self.bot.get_command("corp"))

    async def join_corp(self, ctx, player):
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Join Fleet",
                        value="What is the corp ID for the corp you'd like to join?\n\n")
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120)
        content = msg.content
        sql = ''' SELECT * FROM corporations WHERE `corp_id` = (?) '''
        values = (int(content),)
        corp = await db.select_var(sql, values)
        if len(corp) == 0:
            await ctx.author.send('**ERROR** - No corporation found.')
            return await ctx.invoke(self.bot.get_command("me"), True)
        pending_members = []
        if corp[0][8] is not None:
            pending_members = ast.literal_eval(corp[0][8])
        pending_members.append(player[0])
        pending_members = list(set(pending_members))
        sql = ''' UPDATE corporations
                    SET pending_members = (?)
                    WHERE
                        corp_id = (?); '''
        values = (str(pending_members), int(content))
        await db.execute_sql(sql, values)
        await ctx.author.send('**Success** - Applied to {}.'.format(corp[0][3]))
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
        values = (str(members), fleet[1])
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

    async def kick_member(self, ctx, corp):
        corp_member_dict = {}
        corp_member_array = []
        member_number = 1
        member_count = 0
        members = ast.literal_eval(corp[3])
        for member_id in members:
            sql = ''' SELECT * FROM eve_rpg_players WHERE `id` = (?) '''
            values = (int(member_id),)
            member = await db.select_var(sql, values)
            member_name = self.bot.get_user(int(member[0][2])).display_name
            corp_member_dict[member_number] = member[0][0]
            corp_member_array.append('**{}.** {}'.format(member_number, member_name))
            member_number += 1
        clean_members = '\n'.join(corp_member_array)
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
        members.remove(fleet_member_dict[int(content)])
        sql = ''' UPDATE fleet_info
                    SET fleet_members = (?)
                    WHERE
                        fleet_id = (?); '''
        values = (str(members), fleet[1])
        await db.execute_sql(sql, values)
        await ctx.author.send('**Success** - Member Kicked.')
        await ctx.invoke(self.bot.get_command("me"), True)

    async def review_pending(self, ctx, corp):
        if corp[8] is not None:
            pending_members = ast.literal_eval(corp[8])
        else:
            await ctx.author.send('**ERROR** - No pending applications.')
            return await ctx.invoke(self.bot.get_command("me"), True)
        pending_member_dict = {}
        pending_member_array = []
        member_number = 1
        for pending in pending_members:
            sql = ''' SELECT * FROM eve_rpg_players WHERE `id` = (?) '''
            values = (int(pending),)
            member = await db.select_var(sql, values)
            member_name = self.bot.get_user(int(member[0][2])).display_name
            pending_member_dict[member_number] = member[0][0]
            pending_member_array.append('**{}.** {}'.format(member_number, member_name))
            member_number += 1
        clean_members = '\n'.join(pending_member_array)
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Manage Pending Applications",
                        value="{}".format(clean_members))
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120)
        content = msg.content
        if int(content) not in pending_member_dict:
            await ctx.author.send('**ERROR** - Incorrect Selection.')
            return await ctx.invoke(self.bot.get_command("me"), True)
        applicant = pending_member_dict[int(content)]
        applicant_user = self.bot.get_user(int(applicant[2]))
        applicant_name = applicant_user.display_name
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Manage Pending Applications",
                        value="**Applicant:** {}\n\n"
                              "**1.** Approve\n"
                              "**2.** Deny\n".format(applicant_name))
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120)
        content = msg.content
        if content == '1':
            sql = ''' UPDATE eve_rpg_players
                        SET corp = (?)
                        WHERE
                            id = (?); '''
            values = (corp[1], pending_member_dict[int(content)],)
            await db.execute_sql(sql, values)
            await ctx.author.send('**Member Added**')
            await applicant_user.send('**You have been added to the corporation {}**'.format(corp[3]))
            pending_members = ast.literal_eval(corp[8])
            pending_members.remove(applicant[0])
            pending_members = str(list(set(pending_members)))
            if len(pending_members) == 0:
                pending_members = None
            sql = ''' UPDATE corporations
                        SET pending_members = (?)
                        WHERE
                            corp_id = (?); '''
            values = (str(pending_members), int(content))
            await db.execute_sql(sql, values)
            return
        elif content == '2':
            pending_members = ast.literal_eval(corp[8])
            pending_members.remove(applicant[0])
            pending_members = str(list(set(pending_members)))
            if len(pending_members) == 0:
                pending_members = None
            sql = ''' UPDATE corporations
                        SET pending_members = (?)
                        WHERE
                            corp_id = (?); '''
            values = (str(pending_members), int(content))
            await db.execute_sql(sql, values)
            await ctx.author.send('**Member Denied**')
            await applicant_user.send('**Your application to {} has been denied.**'.format(corp[3]))
            return

    @_corps.group(name='chat')
    @checks.has_account()
    async def _chat(self, ctx, *, message: str):
        """Talk in corp chat."""
        if ctx.guild is not None:
            try:
                await ctx.message.delete()
            except Exception:
                pass
        sql = ''' SELECT * FROM eve_rpg_players WHERE `player_id` = (?) '''
        values = (ctx.message.author.id,)
        player = await db.select_var(sql, values)
        sender = self.bot.get_user(int(player[0][2])).display_name
        sql = ''' SELECT * FROM eve_rpg_players WHERE `fleet` = (?) '''
        values = (int(player[0][16]),)
        fleet_players = await db.select_var(sql, values)
        for user in fleet_players:
            user = self.bot.get_user(int(user[2]))
            await user.send('**Fleet** {}: {}'.format(sender, message))
