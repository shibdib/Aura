from .assets import Assets


def setup(bot):
    bot.add_cog(Assets(bot))
