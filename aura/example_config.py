# bot token from discord developers
# go to https://discordapp.com/developers/applications/me and create an application
# make it a bot user
# put the bot user token below
bot_token = ''

# default bot settings
bot_prefix = ['!']
bot_master = 174764205927432192  # The discord ID of the owner
bot_coowners = [114428861990699012]  # The discord ID's of co-owners

# Auto Responses - Add more with the format 'trigger': 'Auto response'
auto_responses = {
    '1232323': '1234 '
}

# minimum required permissions for bot (Only really needed if you're inviting it to other servers, probably safe to
# not touch this)
bot_permissions = 224256

# Don't touch
preload_extensions = ['eve_rpg', 'set_channels', 'join_game', 'manage_self', 'market', 'travel', 'change_task', 'local',
                      'stats']

