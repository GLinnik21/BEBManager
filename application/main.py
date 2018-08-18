#! /usr/bin/python3.6
import sys
from application import (CLIParser,
                         App)


def main():
    """
    Entry point
    :return:
    """

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
