from discord.ext import commands
from aura.lib import db
from aura.lib import game_functions
from aura.core import checks
from aura.utils import make_embed


class ManageSelf:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session
        self.config = bot.config
        self.logger = bot.logger

    @commands.command(name='me')
    @checks.spam_check()
    @checks.is_whitelist()
    @checks.has_account()
    async def _me(self, ctx):
        """Manage your character."""
        sql = ''' SELECT * FROM eve_rpg_players WHERE `player_id` = (?) '''
        values = (ctx.message.author.id,)
        player = await db.select_var(sql, values)
        player_name = self.bot.get_user(int(player[0][2]))
        region_name = game_functions.get_region(int(player[0][4]))
        current_ship = player[0][15]
        wallet_balance = player[0][5]
        current_task = game_functions.get_task(int(player[0][6]))
        current_focus = game_functions.get_task(int(player[0][7]))
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Welcome {}".format(player_name),
                        value="Current Region - {}\nCurrent Ship - {}\nCurrent Task - {}\nCurrent Focus - {}"
                              "\nWallet Balance - {}\n\n"
                              "User interface initiated.... Select desired action below.\n\n"
                              "**1.** Change task\n"
                              "**2.** Travel to a new region.\n"
                              "**3.** Modify current ship.\n"
                              "**4.** Change into another ship.\n"
                              "**5.** Visit the regional market."
                              "**6.** Change focus\n".format(
                            region_name, current_ship, current_task, current_focus, wallet_balance))
        await ctx.author.send(embed=embed)

        def check(m):
            return m.author == ctx.author

        msg = await self.bot.wait_for('message', check=check)
        content = msg.content
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
