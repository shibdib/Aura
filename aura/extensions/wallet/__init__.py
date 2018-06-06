from .wallet import Wallet


def setup(bot):
    bot.add_cog(Wallet(bot))
