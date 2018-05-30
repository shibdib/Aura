from .travel import Travel


def setup(bot):
    bot.add_cog(Travel(bot))
