from .set_channels import SetChannels


def setup(bot):
    bot.add_cog(SetChannels(bot))
