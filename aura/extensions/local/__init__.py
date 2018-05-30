from .local import Local


def setup(bot):
    bot.add_cog(Local(bot))
