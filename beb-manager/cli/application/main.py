import os
import sys

from application import (CLIParser,
                         config,
                         App)


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
        if args.command == 'current':
            app.print_current_user()
        elif args.command == 'add':
            app.add_user(args.username)
        elif args.command == 'login':
            app.login_user(args.username, args.id)
        elif args.command == 'logout':
            app.logout_user()
        elif args.command == 'all':
            app.print_all_users()
    elif args.object == 'card':
        pass
    elif args.object == 'board':
        if args.command == 'display':
            if args.all:
                app.print_all_boards()
            if args.current:
                app.print_current_board()
            if args.id is not None:
                app.print_board_by_id(args.id)
            if args.name is not None:
                app.print_board_by_name(args.name)
        if args.command == 'add':
            app.add_board(args.name)


if __name__ == '__main__':
    sys.argv = 'beb-manager board display -n New'.split()
    main()
