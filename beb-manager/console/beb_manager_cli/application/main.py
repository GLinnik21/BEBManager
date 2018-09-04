import os
import sys

import beb_manager_cli.application.config as config
from beb_manager_cli.application.app import App
from beb_manager_cli.application.parser import CLIParser


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
    elif args.object == 'board':
        if args.command == 'display':
            if args.all:
                app.print_all_boards()
            elif args.current:
                app.print_current_board()
            else:
                app.print_board(args.id, args.name)
        elif args.command == 'add':
            app.add_board(args.name)
        elif args.command == 'delete':
            app.delete_board(args.id)
        elif args.command == 'edit':
            app.edit_board(args.id, args.name)
        elif args.command == 'switch':
            app.switch_board(args.id)
        elif args.command == 'access':
            mode = args.mode
            if mode[0] == "+":
                app.add_rights(mode[1:], args.user_id, args.board_id)
            elif mode[0] == "~":
                app.remove_rights(mode[1:], args.user_id, args.board_id)
            else:
                print("Invalid \033[4mmode\033[0m format")
                exit(2)
    elif args.object == 'list':
        if args.command == 'display':
            if args.all:
                app.print_all_lists()
            else:
                app.print_list(args.id, args.name)
    elif args.object == 'card':
        pass
    elif args.object == 'tag':
        pass


if __name__ == '__main__':
    main()
