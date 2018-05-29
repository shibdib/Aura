from .join_game import JoinGame


def setup(bot):
    bot.add_cog(JoinGame(bot))
