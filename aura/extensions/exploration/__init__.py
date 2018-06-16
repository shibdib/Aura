from .exploration import Exploration


def setup(bot):
    bot.add_cog(Exploration(bot))
