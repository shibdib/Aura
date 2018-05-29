# bot token from discord developers
# go to https://discordapp.com/developers/applications/me and create an application
# make it a bot user
# put the bot user token below
bot_token = ''

# default bot settings
bot_prefix = ['!']
bot_master = 174764205927432192  # The discord ID of the owner
bot_coowners = [114428861990699012]  # The discord ID's of co-owners

# minimum required permissions for bot (Only really needed if you're inviting it to other servers, probably safe to
# not touch this)
bot_permissions = 224256

# Add any extensions to the below preload_extentions array to always load them on restart. Note that extensions can be
# loaded on demand using the !ext load command.
preload_extensions = [
    # 'killmails',  # Killmail posting extension
    # 'add_kills',  # Enables the addkills command
    'eve_time',  # Get the time in eve and around the world
    'eve_status',  # Get the status of the server and the player count
    'price',  # Price check extension
    'group_lookup',  # Get corp/alliance info
    'char_lookup',  # Get character info
    'jump_planner',  # Provides the shortcut for dotlan jump planning
    'jump_range',  # Provides the shortcut for dotlan jump range
    'location_scout',  # Provides intel on systems/constellations/regions
    # 'sov_tracker',  # Provides real time info on sov fights
    # 'fleet_up',  # Shares upcoming fleet-up operations
    # The following plugins are still in testing, use at your own risk
    # The following plugins require access tokens, please read the wiki for more information
    # 'tokens',  # This extension is required if using any plugins that require tokens
    # 'eve_notifications',  # Shares notifications
    # 'eve_mail',  # Shares mail
    # 'stream_player',  # Play youtube and other streams in a voice channel
    # 'jabber_relay'  # Completely broken, dont use me yet
]

