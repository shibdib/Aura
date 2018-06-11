from .corps import Corps


def setup(bot):
    bot.add_cog(Corps(bot))
