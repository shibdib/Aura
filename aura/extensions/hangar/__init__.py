from .hangar import Hangar


def setup(bot):
    bot.add_cog(Hangar(bot))
