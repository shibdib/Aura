"""Aura - An EVE Online Discord RPG Bot"""

import argparse
import asyncio
import sys

import discord
from aura.core import bot, events
from aura.utils import logger
from aura.utils import ExitCodes

if discord.version_info.major < 1:
    print("You are not running discord.py v1.0.0a or above.\n\n"
          "aura requires the new discord.py library to function "
          "correctly. Please install the correct version.")
    sys.exit(1)


def run_aura(debug=None, launcher=None):
    aura = bot.Aura()
    events.init_events(aura, launcher=launcher)
    aura.logger = logger.init_logger(debug_flag=debug)
    aura.load_extension('aura.core.commands')
    aura.load_extension('aura.core.extension_manager')
    for ext in aura.preload_ext:
        ext_name = ("aura.extensions." + ext)
        aura.load_extension(ext_name)
    loop = asyncio.get_event_loop()
    if aura.token is None or not aura.default_prefix:
        aura.logger.critical("Token and prefix must be set in order to login.")
        sys.exit(1)
    try:
        loop.run_until_complete(aura.start(aura.token))
    except discord.LoginFailure:
        aura.logger.critical("Invalid token")
        loop.run_until_complete(aura.logout())
        aura._shutdown_mode = ExitCodes.SHUTDOWN
    except KeyboardInterrupt:
        aura.logger.info("Keyboard interrupt detected. Quitting...")
        loop.run_until_complete(aura.logout())
        aura._shutdown_mode = ExitCodes.SHUTDOWN
    except Exception as e:
        aura.logger.critical("Fatal exception", exc_info=e)
        loop.run_until_complete(aura.logout())
    finally:
        code = aura._shutdown_mode
        sys.exit(code.value)


def parse_cli_args():
    parser = argparse.ArgumentParser(
        description="Aura - An EVE Online Discord RPG Bot")
    parser.add_argument(
        "--debug", "-d", help="Enabled debug mode.", action="store_true")
    parser.add_argument(
        "--launcher", "-l", help=argparse.SUPPRESS, action="store_true")
    return parser.parse_args()


def main():
    args = parse_cli_args()
    run_aura(debug=args.debug, launcher=args.launcher)


if __name__ == '__main__':
    main()
