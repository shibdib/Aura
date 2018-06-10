from .fleets import Fleets


def setup(bot):
    bot.add_cog(Fleets(bot))
