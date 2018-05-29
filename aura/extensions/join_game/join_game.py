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
        embed = make_embed(guild=ctx.guild)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Welcome",
                        value='Welcome to the game! You need to respond to a few simple questions to get started.\n\n'
                              'Questions are multiple choice and you respond by messaging the number of your choice.')
        await ctx.author.send(embed=embed)
        await ctx.author.send('**Question One\n\nChoose your race.\n**1.**Caldari\n**2.**Amarr\n**3.**Minmatar\n'
                              '**4.**Gallente\n**5.**Jove**')

        def check(m):
            return m.channel == ctx.author

        msg = await self.bot.wait_for('message', check=check)
        response = 'ERROR'
        if msg == '1':
            response = 'You chose Caldari'
        elif msg == '2':
            response = 'You chose Amarr'
        elif msg == '3':
            response = 'You chose Minmatar'
        elif msg == '4':
            response = 'You chose Gallente'
        elif msg == '5':
            response = 'You chose Jove'
        await ctx.author.send(response)
