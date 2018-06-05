from discord.ext import commands

from aura.core import checks
from aura.lib import db
from aura.utils import make_embed


class GameModerator:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session
        self.config = bot.config
        self.logger = bot.logger

    @commands.group(name='gm', case_insensitive=True)
    @checks.is_co_owner()
    @checks.has_account()
    async def _gm(self, ctx):
        """Change your current task."""
        if ctx.invoked_subcommand is None:
            if ctx.guild is not None:
                try:
                    await ctx.message.delete()
                except Exception:
                    pass
            embed = make_embed(icon=ctx.bot.user.avatar)
            embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                             text="Aura - EVE Text RPG")
            embed.add_field(name="Local List",
                            value="**1.** Give ISK.\n"
                                  "**2.** Set ISK.\n"
                                  "**3.** Warn Player.\n"
                                  "**4.** Ban Player.\n")
            await ctx.author.send(embed=embed)

            def check(m):
                return m.author == ctx.author and m.channel == ctx.author.dm_channel

            msg = await self.bot.wait_for('message', check=check, timeout=120.0)
            content = msg.content
            if content == '1':
                await self.give_isk(ctx)
            elif content == '2':
                await self.set_isk(ctx)
            elif content == '3':
                await self.warn_player(ctx)
            elif content == '4':
                await self.ban_player(ctx)
            else:
                return await ctx.author.send('**ERROR** - Not a valid choice.')

    async def give_isk(self, ctx):
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Give ISK",
                        value="Send the player ID")
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120.0)
        player = msg.content
        sql = ''' SELECT * FROM eve_rpg_players WHERE `player_id` = (?) '''
        values = (int(player),)
        result = await db.select_var(sql, values)
        if len(result) == 0:
            return await ctx.author.send('**ERROR** - No player found.')
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Give ISK",
                        value="How much ISK would you like to give them?")
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120.0)
        isk = msg.content
        cost = '{0:,.2f}'.format(float(isk))
        embed = make_embed(icon=ctx.bot.user.avatar)
        receiver = self.bot.get_user(int(result[0][2]))
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Confirmation",
                        value="Confirm you want to give {} {} ISK\n\n**1.** Yes\n**2.** No".format(
                            receiver.display_name, cost))
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120.0)
        response = msg.content
        if response != '1':
            return await ctx.author.send('**Canceled**')
        sql = ''' UPDATE eve_rpg_players
                SET isk = (?)
                WHERE
                    player_id = (?); '''
        new_isk = float(result[0][5]) + float(isk)
        values = (int(float(new_isk)), result[0][2],)
        await db.execute_sql(sql, values)
        self.logger.info('GM - {} sent {} {} ISK'.format(ctx.author.display_name, receiver, isk))
        await receiver.send('A member of the GM team has added {} ISK to your wallet.'.format(cost))
        return await ctx.author.send('**ISK Sent**')

    async def set_isk(self, ctx):
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Give ISK",
                        value="Send the player ID")
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120.0)
        player = msg.content
        sql = ''' SELECT * FROM eve_rpg_players WHERE `player_id` = (?) '''
        values = (int(player),)
        result = await db.select_var(sql, values)
        if len(result) == 0:
            return await ctx.author.send('**ERROR** - No player found.')
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Give ISK",
                        value="How much ISK would you like to set them at?")
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120.0)
        isk = msg.content
        cost = '{0:,.2f}'.format(float(isk))
        embed = make_embed(icon=ctx.bot.user.avatar)
        receiver = self.bot.get_user(int(result[0][2]))
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Confirmation",
                        value="Confirm you want to set {} at {} ISK\n\n**1.** Yes\n**2.** No".format(
                            receiver.display_name, cost))
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120.0)
        response = msg.content
        if response != '1':
            return await ctx.author.send('**Canceled**')
        sql = ''' UPDATE eve_rpg_players
                SET isk = (?)
                WHERE
                    player_id = (?); '''
        values = (int(float(isk)), result[0][2],)
        await db.execute_sql(sql, values)
        self.logger.info('GM - {} set {} to {} ISK'.format(ctx.author.display_name, receiver, isk))
        await receiver.send('A member of the GM team has reset your wallet to {} ISK.'.format(cost))
        return await ctx.author.send('**ISK Sent**')

    async def warn_player(self, ctx):
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Warn Player",
                        value="Send the player ID")
        await ctx.author.send(embed=embed)

    async def ban_player(self, ctx):
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Ban Player",
                        value="Send the player ID")
        await ctx.author.send(embed=embed)

    @_gm.group(name='global')
    @checks.is_co_owner()
    @checks.has_account()
    async def _chat(self, ctx, *, message: str):
        """Talk in global."""
        if ctx.guild is not None:
            await ctx.message.delete()
        sql = ''' SELECT * FROM eve_rpg_players WHERE `player_id` = (?) '''
        values = (ctx.message.author.id,)
        player = await db.select_var(sql, values)
        sender = self.bot.get_user(int(player[0][2])).display_name
        await self.send_global('**GLOBAL** GM {}: {}'.format(sender, message))

    async def send_global(self, message, embed=False):
        sql = "SELECT * FROM eve_rpg_channels"
        game_channels = await db.select(sql)
        for channels in game_channels:
            channel = self.bot.get_channel(int(channels[2]))
            if channel is None:
                await self.remove_bad_channel(channels[2])
                continue
            if embed is False:
                await channel.send(message)
                continue
            else:
                await channel.send(embed=message)
                continue
        sql = "SELECT * FROM eve_rpg_players"
        players = await db.select(sql)
        for player in players:
            channel = self.bot.get_user(player[2])
            if channel is None:
                await self.remove_bad_user(player[2])
                continue
            if embed is False:
                await channel.send(message)
                continue
            else:
                await channel.send(embed=message)
                continue

    async def remove_bad_user(self, player_id):
        sql = ''' DELETE FROM eve_rpg_players WHERE `player_id` = (?) '''
        values = (player_id,)
        await db.execute_sql(sql, values)
        return self.logger.info('eve_rpg - Bad player removed successfully')

    async def remove_bad_channel(self, channel_id):
        sql = ''' DELETE FROM eve_rpg_channels WHERE `channel_id` = (?) '''
        values = (channel_id,)
        await db.execute_sql(sql, values)
        return self.logger.info('eve_rpg - Bad Channel removed successfully')
