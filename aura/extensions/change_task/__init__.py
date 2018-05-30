from .change_task import ChangeTask


def setup(bot):
    bot.add_cog(ChangeTask(bot))
