from discord.ext import commands

from aura.core import checks
from aura.lib import db


class SetChannels:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session
        self.config = bot.config
        self.logger = bot.logger

    @commands.command(name='setRpg')
    @checks.is_mod()
    async def _set_rpg(self, ctx):
        """Sets a channel as an RPG channel.
        Do **!setRpg** to have a channel relay all RPG events.
        The RPG includes players from all servers this instance of the bot is on."""
        sql = ''' REPLACE INTO eve_rpg_channels(server_id,channel_id,owner_id)
                  VALUES(?,?,?) '''
        author = ctx.message.author.id
        channel = ctx.message.channel.id
        server = ctx.message.guild.id
        values = (server, channel, author)
        await db.execute_sql(sql, values)
        self.logger.info('eve_rpg - {} added {} to the rpg channel list.')
        return await ctx.author.send('**Success** - Channel added.')