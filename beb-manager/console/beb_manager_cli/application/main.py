import os

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
        if args.command == 'show':
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
                app.add_board_rights(mode[1:], args.user_id, args.board_id)
            elif mode[0] == "~":
                app.remove_board_rights(mode[1:], args.user_id, args.board_id)
    elif args.object == 'list':
        if args.command == 'show':
            if args.all:
                app.print_all_lists()
            else:
                app.print_list(args.id, args.name)
        elif args.command == 'add':
            app.add_list(args.name)
        elif args.command == 'edit':
            app.edit_list(args.id, args.name)
        elif args.command == 'delete':
            app.delete_list(args.id)
        elif args.command == 'access':
            mode = args.mode
            if mode[0] == "+":
                app.add_list_rights(mode[1:], args.user_id, args.list_id)
            elif mode[0] == "~":
                app.remove_list_rights(mode[1:], args.user_id, args.list_id)
    elif args.object == 'card':
        if args.command == 'show':
            if args.id is not None:
                app.print_card(args.id, None)
            elif args.name is not None:
                app.print_card(None, args.name)
            elif args.created is not None:
                app.print_created()
            elif args.assigned is not None:
                app.print_assigned()
            elif args.archived is not None:
                app.print_archived()
            elif args.can_read is not None:
                app.print_readable_cards()
            elif args.can_write is not None:
                app.print_writable_cards()
        elif args.command == 'add':
            app.add_card(name=args.name,
                         list_id=args.list_id,
                         list_name=args.list_name,
                         description=args.description,
                         priority=args.priority,
                         tags=args.tags,
                         children=args.children,
                         exp_date=args.expiration_date,
                         repeat=args.repeat,
                         start=args.start_repeat_at)
        elif args.command == 'edit':
            app.edit_card(card_id=args.card_id,
                          name=args.name,
                          list_id=args.list_id,
                          list_name=args.list_name,
                          description=args.description,
                          priority=args.priority,
                          add_tags=args.add_tags,
                          remove_tags=args.remove_tags,
                          add_children=args.add_children,
                          remove_children=args.remove_children,
                          exp_date=args.expiration_date,
                          delete_plan=args.delete_args,
                          repeat=args.repeat,
                          start=args.start_repeat_at)
        elif args.command == 'delete':
            app.delete_card(args.id)
        elif args.command == 'archive':
            app.archive_card(args.id)
        elif args.command == 'assign':
            app.assign_card(args.card_id, args.user_id)
        elif args.command == 'access':
            mode = args.mode
            if mode[0] == "+":
                app.add_card_rights(mode[1:], args.user_id, args.list_id)
            elif mode[0] == "~":
                app.remove_card_rights(mode[1:], args.user_id, args.list_id)
    elif args.object == 'tag':
        pass


if __name__ == '__main__':
    main()
