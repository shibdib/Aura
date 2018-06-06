from .contacts import Contacts


def setup(bot):
    bot.add_cog(Contacts(bot))
