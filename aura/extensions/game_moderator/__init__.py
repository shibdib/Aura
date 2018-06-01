from .game_moderator import GameModerator


def setup(bot):
    bot.add_cog(GameModerator(bot))
