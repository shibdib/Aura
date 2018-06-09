import ast

from discord.ext import commands

from aura.core import checks
from aura.lib import db
from aura.utils import make_embed


class Contacts:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session
        self.config = bot.config
        self.logger = bot.logger

    @commands.command(name='contacts', case_insensitive=True)
    @checks.spam_check()
    @checks.is_whitelist()
    @checks.has_account()
    async def _contacts(self, ctx):
        """View your contact list."""
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
            blue_array = []
            if player[0][21] is not None:
                for user in ast.literal_eval(player[0][21]):
                    sql = ''' SELECT * FROM eve_rpg_players WHERE `id` = (?) '''
                    values = (user,)
                    blue = await db.select_var(sql, values)
                    if len(blue) > 0:
                        blue_name = self.bot.get_user(int(blue[0][2])).display_name
                        blue_array.append(blue_name)
                    else:
                        continue
                blue_text = '\n'.join(blue_array)
            else:
                blue_text = ''
            embed = make_embed(icon=ctx.bot.user.avatar)
            embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                             text="Aura - EVE Text RPG")
            embed.add_field(name="{}'s Contacts".format(player_name),
                            value="__**Blues**__\n{}\n\n**1.** Add user to the blue list\n"
                                  "**2.** Remove a user from the blue list\n"
                                  "**3.** Return to the main menu".format(blue_text))
            await ctx.author.send(embed=embed)

            def check(m):
                return m.author == ctx.author and m.channel == ctx.author.dm_channel

            msg = await self.bot.wait_for('message', check=check, timeout=120)
            content = msg.content
            if content == '1':
                await self.add_blue(ctx, player[0])
            elif content == '2':
                await self.remove_blue(ctx, player[0])
            elif content == '3':
                await ctx.invoke(self.bot.get_command("me"), True)
            elif '!!' not in content:
                await ctx.author.send('**ERROR** - Not a valid choice.')
                if content.find('!!') == -1:
                    return await ctx.invoke(self.bot.get_command("me"), True)
                else:
                    return

    async def add_blue(self, ctx, player):
        player_name = self.bot.get_user(int(player[2])).display_name
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Add Contacts".format(player_name),
                        value="What is the player ID of the user you'd like to add?\n\n"
                              "*Users can find their player ID on the top of their !!me menu*")
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120)
        content = msg.content
        sql = ''' SELECT * FROM eve_rpg_players WHERE `id` = (?) '''
        values = (int(content),)
        new_blue = await db.select_var(sql, values)
        if len(new_blue) == 0:
            await ctx.author.send('**ERROR** - Not a valid player.')
            return await ctx.invoke(self.bot.get_command("me"), True)
        blue_name = self.bot.get_user(int(new_blue[0][2])).display_name
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Add Contacts".format(player_name),
                        value="Confirm you want to add **{}** to your blue list.\n\n"
                              "*Players on your blue list will not be attacked by you, they will still attack you "
                              "unless they also add you to their blues list*\n\n"
                              "**1.** Yes\n"
                              "**2.** No".format(blue_name))
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120)
        content = msg.content
        if int(content) != 1:
            await ctx.author.send('**New Contact Canceled**')
            if content.find('!!') == -1:
                return await ctx.invoke(self.bot.get_command("me"), True)
            else:
                return
        if player[21] is not None:
            blue_array = ast.literal_eval(player[21])
            blue_array.append(new_blue[0][0])
        else:
            blue_array = [new_blue[0][0]]
        sql = ''' UPDATE eve_rpg_players
                    SET blue_players = (?)
                    WHERE
                        player_id = (?); '''
        values = (str(blue_array), ctx.author.id,)
        await db.execute_sql(sql, values)
        await ctx.author.send('**Success** - {} is now blue.'.format(blue_name))
        await ctx.invoke(self.bot.get_command("me"), True)

    async def remove_blue(self, ctx, player):
        if player[0][21] is not None:
            remove_blue = {}
            remove_text = []
            count = 1
            for user in ast.literal_eval(player[0][21]):
                sql = ''' SELECT * FROM eve_rpg_players WHERE `id` = (?) '''
                values = (user,)
                blue = await db.select_var(sql, values)
                blue_name = self.bot.get_user(int(blue[0][2])).display_name
                remove_blue[count] = {'name': blue_name, 'id': user, 'selection': count}
                remove_text.append('**{}.** {}'.format(count, blue_name))
            blue_text = '\n'.join(remove_text)
        else:
            await ctx.author.send('**ERROR** - You have no one to remove.')
            return await ctx.invoke(self.bot.get_command("me"), True)
        player_name = self.bot.get_user(int(player[2])).display_name
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Remove Contacts".format(player_name),
                        value="Select the user you'd like to remove\n\n{}".format(blue_text))
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120)
        content = msg.content
        if int(content) not in remove_blue:
            await ctx.author.send('**ERROR** - Incorrect Selection.')
            if content.find('!!') == -1:
                return await ctx.invoke(self.bot.get_command("me"), True)
            else:
                return
        sql = ''' SELECT * FROM eve_rpg_players WHERE `id` = (?) '''
        values = (remove_blue[int(content)]['id'],)
        blue = await db.select_var(sql, values)
        blue_name = self.bot.get_user(int(blue[0][2])).display_name
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Add Contacts".format(player_name),
                        value="Confirm you want to remove **{}** from your blue list.\n\n"
                              "*You will freely engage this player if you encounter them*\n\n"
                              "**1.** Yes\n"
                              "**2.** No".format(blue_name))
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120)
        confirm = msg.content
        if int(confirm) != 1:
            await ctx.author.send('**Removal Canceled**')
            if content.find('!!') == -1:
                return await ctx.invoke(self.bot.get_command("me"), True)
            else:
                return
        blue_array = ast.literal_eval(player[21])
        blue_array.remove(remove_blue[int(content)]['id'])
        sql = ''' UPDATE eve_rpg_players
                    SET blue_players = (?)
                    WHERE
                        player_id = (?); '''
        values = (str(blue_array), ctx.author.id,)
        await db.execute_sql(sql, values)
        await ctx.author.send('**Success** - {} is no longer blue.'.format(blue_name))
        await ctx.invoke(self.bot.get_command("me"), True)
