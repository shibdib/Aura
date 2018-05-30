from discord.ext import commands
from aura.lib import db
from aura.core import checks
from aura.utils import make_embed


class JoinGame:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session
        self.config = bot.config
        self.logger = bot.logger

    @commands.command(name='join')
    @checks.spam_check()
    @checks.is_whitelist()
    async def _rpg(self, ctx):
        """Sign up for the RPG.
        If your server doesn't have an RPG channel have an admin do **!setRpg** to receive the game events.
        **If you've already registered this will reset your account.**"""
        #  Check if user exists already and confirm restart
        sql = ''' SELECT id FROM eve_rpg_players WHERE `player_id` = (?) '''
        values = (ctx.message.author.id,)
        result = await db.select_var(sql, values)
        if result is None or len(result) is 0:
            embed = make_embed(icon=ctx.bot.user.avatar)
            embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                             text="Aura - EVE Text RPG")
            embed.add_field(name="WARNING",
                            value="You already have an active account are you sure you want to reset?\n\n"
                                  "**1.** Yes Reset My Account\n"
                                  "**2.** No!!")
            await ctx.author.send(embed=embed)

            def check(m):
                return m.author == ctx.author and m.channel == ctx.author.dm_channel

            msg = await self.bot.wait_for('message', check=check, timeout=120.0)
            content = msg.content
            if content != '1':
                return
        sql = ''' REPLACE INTO eve_rpg_players(server_id,player_id)
                  VALUES(?,?) '''
        author = ctx.message.author.id
        if ctx.guild is None:
            return await ctx.author.send('WARNING: The join command cannot be done via a DM.')
        await ctx.message.delete()
        server = ctx.message.guild.id
        values = (server, author)
        await db.execute_sql(sql, values)
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Welcome",
                        value="Welcome to the game!\nI'm Aura, I will be your key to interacting with the game world."
                              "\nYou need to respond to a few simple questions to get started.\n\n"
                              "Questions are multiple choice and you respond by messaging the number of your choice.")
        #  Race
        embed.add_field(name="Question One",
                        value='Choose your race.\n**1.** Caldari\n**2.** Amarr\n**3.** Minmatar\n'
                              '**4.** Gallente')
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        msg = await self.bot.wait_for('message', check=check, timeout=120.0)
        content = msg.content
        race = 'Caldari'
        ship = 'Ibis'
        ship_id = 1
        region = 'The Forge'
        region_id = 1
        if content == '1':
            race = 'Caldari'
            ship = 'Ibis'
            ship_id = 1
            region = 'The Forge'
            region_id = 1
        elif content == '2':
            race = 'Amarr'
            ship = 'Impairor'
            ship_id = 2
            region = 'Domain'
            region_id = 2
        elif content == '3':
            race = 'Minmatar'
            ship = 'Reaper'
            ship_id = 3
            region = 'Heimatar'
            region_id = 3
        elif content == '4':
            race = 'Gallente'
            ship = 'Velator'
            ship_id = 5
            region = 'Essence'
            region_id = 4
        elif content == '99':
            race = 'Jove'
            ship = 'Specter'
            ship_id = 5
            region = 'The Forge'
            region_id = 1
        sql = ''' UPDATE eve_rpg_players
                SET race = (?),
                    ship = (?),
                    region = (?)
                WHERE
                    player_id = (?); '''
        values = (int(content), ship_id, region_id, author,)
        await db.execute_sql(sql, values)
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name=race,
                        value='Good choice, your race determines the ship you start with (and receive upon death) '
                              'along with your starting region.\n**Starting Ship** - {}\n**Home Region** - {}'.format(
                               ship, region))
        await ctx.author.send(embed=embed)
        embed = make_embed(icon=ctx.bot.user.avatar_url)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name='Gameplay',
                        value='Initial setup is now complete. Your pilot is currently docked in your home region and '
                              'is awaiting your guidance. To interact with your character do *!me*.')
        await ctx.author.send(embed=embed)
        await self.send_global('**New Player** {} has joined the game.'.format(ctx.author.display_name))
        self.logger.info('eve_rpg - ' + str(ctx.message.author) + ' added to the game.')

    async def send_global(self, message, embed=False):
        sql = "SELECT * FROM eve_rpg_channels"
        game_channels = await db.select(sql)
        for channels in game_channels:
            channel = self.bot.get_channel(int(channels[2]))
            if channel is None:
                self.logger.exception('eve_rpg - Bad Channel Attempted removing....')
                await self.remove_bad_channel(channels[2])
            if embed is False:
                await channel.send(message)
            else:
                await channel.send(embed=message)

    async def remove_bad_channel(self, channel_id):
        sql = ''' DELETE FROM eve_rpg_channels WHERE `channel_id` = (?) '''
        values = (channel_id,)
        await db.execute_sql(sql, values)
        return self.logger.info('eve_rpg - Bad Channel removed successfully')
