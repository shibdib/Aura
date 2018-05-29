from .manage_self import ManageSelf


def setup(bot):
    bot.add_cog(ManageSelf(bot))
