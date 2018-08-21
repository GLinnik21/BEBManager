#! /usr/bin/python3.6
import os
import sys
from application import (CLIParser,
                         App,
                         config)


def main():
    """
    Entry point
    :return:
    """

    if not os.path.exists(config.APP_DATA_DIRECTORY):
        os.makedirs(config.APP_DATA_DIRECTORY)

    parser = CLIParser()
    args = parser.parse()
    app = App()

    if args.object == 'user':
        if args.command == 'add':
            app.add_user(args.name)
    elif args.object == 'card':
        pass


if __name__ == '__main__':
    sys.argv = "beb user add Beb".split()
    main()
