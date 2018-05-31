from .ship_fitting import ShipFitting


def setup(bot):
    bot.add_cog(ShipFitting(bot))
