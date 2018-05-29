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
        sql = ''' REPLACE INTO eve_rpg_players(server_id,player_id)
                  VALUES(?,?) '''
        author = ctx.message.author.id
        server = ctx.message.guild.id
        values = (server, author)
        await db.execute_sql(sql, values)
        self.logger.info('eve_rpg - ' + str(ctx.message.author) + ' added to the game.')
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
                              '**4.** Gallente\n**5.** Jove')
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author

        msg = await self.bot.wait_for('message', check=check)
        content = msg.content
        race = 'Caldari'
        ship = 'Ibis'
        region = 'The Forge'
        region_id = 1
        if content == '1':
            race = 'Caldari'
            ship = 'Ibis'
            region = 'The Forge'
            region_id = 1
        elif content == '2':
            race = 'Amarr'
            ship = 'Impairor'
            region = 'Domain'
            region_id = 2
        elif content == '3':
            race = 'Minmatar'
            ship = 'Reaper'
            region = 'Heimatar'
            region_id = 3
        elif content == '4':
            race = 'Gallente'
            ship = 'Velator'
            region = 'Essence'
            region_id = 4
        elif content == '5':
            race = 'Jove'
            ship = 'Specter'
            region = 'The Forge'
            region_id = 1
        sql = ''' UPDATE eve_rpg_players
                SET race = (?),
                    ship = (?),
                    region = (?)
                WHERE
                    player_id = (?); '''
        values = (int(content), ship, region_id, author,)
        await db.execute_sql(sql, values)
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name=race,
                        value='Good choice, your race determines the ship you start with (and receive upon death) '
                              'along with your starting region.\n**Starting Ship** - {}\n**Home Region** - {}'.format(
                               ship, region))
        #  Profession
        embed.add_field(name="Question Two",
                        value='Choose your initial focus (You can change this later).\n**1.** PVP\n'
                              '**2.** PVE\n**3.** Mining\n**4.** Industry')
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author

        msg = await self.bot.wait_for('message', check=check)
        content = msg.content
        response = 'ERROR'
        if content == '1':
            response = 'You chose the life of a PVPer.'
        elif content == '2':
            response = 'You chose to be a PVE focused pilot.'
        elif content == '3':
            response = 'You chose mining.'
        elif content == '4':
            response = 'You chose to be an industrialist.'
        sql = ''' UPDATE eve_rpg_players
                SET role = (?)
                WHERE
                    player_id = (?); '''
        values = (int(content), author,)
        await db.execute_sql(sql, values)
        embed = make_embed(icon=ctx.bot.user.avatar_url)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name='Focus',
                        value='Interesting, {} Your focus determines what your pilot does in the game, this can be '
                              'changed at any time and more focuses become available as you advance.'.format(response))
        embed.add_field(name='Gameplay',
                        value='Initial setup is now complete. Your pilot is currently docked in your home region and '
                              'is awaiting your guidance. To interact with your character do *!me*.')
        await ctx.author.send(embed=embed)
