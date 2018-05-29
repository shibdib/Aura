import sys
import os
import argparse
import subprocess


class ArgumentParser(argparse.ArgumentParser):
    def __is_valid_directory(self, parser, arg):
        if not os.path.isdir(arg):
            parser.error('Directory {} not found.'.format(arg))
        else:
            return arg

    def add_argument_with_dir_check(self, *args, **kwargs):
        kwargs['type'] = lambda x: self.__is_valid_directory(self, x)
        self.add_argument(*args, **kwargs)


def parse_cli_args():
    parser = ArgumentParser(
        description="Aura - An EVE Online Discord RPG Bot")
    parser.add_argument(
        "--no-restart", "-r",
        help="Disables auto-restart.", action="store_true")
    parser.add_argument(
        "--debug", "-d", help="Enabled debug mode.", action="store_true")
    return parser.parse_known_args()


def main():
    print('''
  .--.  .-. .-.,---.    .--.   \n
 / /\ \ | | | || .-.\  / /\ \  \n
/ /__\ \| | | || `-'/ / /__\ \ \n
|  __  || | | ||   (  |  __  | \n
| |  |)|| `-')|| |\ \ | |  |)| \n
|_|  (_)`---(_)|_| \)\|_|  (_) \n
                   (__)        \n
''')

    if sys.version_info < (3, 5, 0):
        print("ERROR: Minimum Python version not met.\n"
              "Aura requires Python 3.5 or higher.\n")
        return

    print("Launching Aura...", end=' ', flush=True)

    launch_args, ft_args = parse_cli_args()

    if launch_args.debug:
        ft_args.append('-d')

    # Get environment
    env = os.environ

    ft_args.append('-l')

    while True:
        code = subprocess.call(["Aura-bot", *ft_args], env=env)
        if code == 0:
            print("Goodbye!")
            break
        elif code == 26:
            print("Rebooting! I'll be back in a bit!\n")
            continue
        else:
            if launch_args.no_restart:
                break
            print("I crashed! Trying to restart...\n")
    print("Exit code: {exit_code}".format(exit_code=code))
    sys.exit(code)


if __name__ == '__main__':
    main()
