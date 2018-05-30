from discord.ext import commands
from aura.lib import db
from aura.lib import game_functions
from aura.core import checks
from aura.utils import make_embed


class Local:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session
        self.config = bot.config
        self.logger = bot.logger

    @commands.command(name='local', case_insensitive=True)
    @checks.spam_check()
    @checks.is_whitelist()
    @checks.has_account()
    async def local_list(self, ctx):
        """Change your current task."""
        if ctx.guild is not None:
            await ctx.message.delete()
        sql = ''' SELECT * FROM eve_rpg_players WHERE `player_id` = (?) '''
        values = (ctx.message.author.id,)
        player = await db.select_var(sql, values)
        region_id = int(player[0][4])
        sql = ''' SELECT * FROM eve_rpg_players WHERE `region` = (?) '''
        values = (region_id,)
        local_players = await db.select_var(sql, values)
        local_array = []
        for user in local_players:
            user_name = self.bot.get_user(int(user[2])).display_name
            docked = ''
            if user[6] == 1:
                docked = '**Docked**'
            local_array.append('{} {}'.format(user_name, docked))
        local_list = '\n'.join(local_array)
        embed = make_embed(icon=ctx.bot.user.avatar)
        embed.set_footer(icon_url=ctx.bot.user.avatar_url,
                         text="Aura - EVE Text RPG")
        embed.add_field(name="Local List",
                        value="{}".format(local_list))
        await ctx.author.send(embed=embed)