import argparse
from datetime import datetime


class ValidateDateAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        try:
            datetime.strptime(values, '%Y-%m-%d,%H:%M')
            namespace.expiration_date = values
        except ValueError:
            try:
                datetime.strptime(values, '%Y-%m-%d')
                namespace.expiration_date = values + ",9:00"
            except ValueError:
                parser.error("Not valid date: '{}'.".format(values))


class ValidateStartAtUsageAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if namespace.repeat is None:
            parser.error("[-sa START_REPEAT_AT] should be used only with [-r REPEAT]")
        else:
            namespace.start_repeat_at = values


class ValidateAccessModeAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values.startswith("+") or values.startswith("~"):
            if len(values[1:]) == 2:
                if values[1:] == 'rw' or values[1:] == 'wr':
                    namespace.mode = values
                    return
            elif len(values[1:]) == 1:
                if values[1:] == 'r' or values[1:] == 'w':
                    namespace.mode = values
                    return

        parser.error("Invalid \033[4mmode\033[0m format")


class CLIParser:

    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Achieve your goals with BebSelf issues tracker')
        self.object_subparsers = self.parser.add_subparsers(dest='object',
                                                            metavar="<object>",
                                                            title="available objects are")
        self.object_subparsers.required = True

        self._add_all_parsers()

    def parse(self, args=None):
        args = self.parser.parse_args(args)
        return args

    def _add_all_parsers(self):
        self._add_user_parser()
        self._add_board_parser()
        self._add_list_parser()
        self._add_card_parser()
        self._add_tag_parser()

    def _add_card_parser(self):
        card_parser = self.object_subparsers.add_parser('card',
                                                        description="Operate cards. Cards are the basic structure "
                                                                    "that's meant to represent one task",
                                                        help="Operate cards. Cards are the basic structure "
                                                             "that's meant to represent one task")
        card_subparsers = card_parser.add_subparsers(dest='command',
                                                     metavar="<command>",
                                                     title="commands that applicable to cards")
        card_subparsers.required = True

        cards_creation_parser = card_subparsers.add_parser('add', description='Add card', help='add card')
        cards_creation_list_group = cards_creation_parser.add_mutually_exclusive_group()
        cards_creation_list_group.required = True

        cards_creation_parser.add_argument('name', help='name of the new card')
        cards_creation_list_group.add_argument('-lid', '--list_id', type=int,
                                               help='unique id of list where the card would be stored')
        cards_creation_list_group.add_argument('-ln', '--list_name',
                                               help='name of list where the card would be stored')

        cards_creation_parser.add_argument('-d', '--description', help='description of the task in the card')
        cards_creation_parser.add_argument('-p', '--priority', choices=['low', 'medium', 'high'], default='medium',
                                           help='priority of the card (default is "medium")')
        cards_creation_parser.add_argument('-t', '--tags', help='names of the tags to add', nargs='*')
        cards_creation_parser.add_argument('-c', '--children', help='ids of the children cards', type=int, nargs='*')
        cards_creation_parser.add_argument("-e", "--expiration_date",
                                           help="The Expiration Date - format YYYY-MM-DD,hh:mm",
                                           action=ValidateDateAction)
        cards_creation_plan_group = cards_creation_parser.add_argument_group('plan',
                                                                             'Arguments to configure periodical task')
        cards_creation_plan_group.required = False
        cards_creation_plan_group.add_argument('-r',
                                               '--repeat',
                                               help="Creates repeated card according to interval. E.g. repeat '1 week'")
        cards_creation_plan_group.add_argument('-sa',
                                               '--start_repeat_at',
                                               help="Start date time for repeated card. E.g. --sa 'in 3 days'",
                                               action=ValidateStartAtUsageAction)

        card_editing_parser = card_subparsers.add_parser('edit', description='Change card', help='change card')
        cards_editing_list_group = card_editing_parser.add_mutually_exclusive_group()

        card_editing_parser.add_argument('card_id', type=int,
                                         help='unique identifier of the card that should be edited')
        cards_editing_list_group.add_argument('-lid', '--list_id', type=int,
                                              help='unique id of list where the card would be stored')
        cards_editing_list_group.add_argument('-ln', '--list_name',
                                              help='name of list where the card would be stored')
        card_editing_parser.add_argument('-n', '--name', help='new name of the new card')

        card_editing_parser.add_argument('-d', '--description', help='new description of the task in the card')
        card_editing_parser.add_argument('-p', '--priority', choices=['low', 'medium', 'high'],
                                         help='new priority of the card')
        card_editing_parser_tag_group = card_editing_parser.add_mutually_exclusive_group()
        card_editing_parser_tag_group.add_argument('-at', '--add_tags', help='name of the tags to add', nargs='*')
        card_editing_parser_tag_group.add_argument('-rt', '--remove_tags', help='name of the tags to remove', nargs='*')
        card_editing_parser_children_group = card_editing_parser.add_mutually_exclusive_group()
        card_editing_parser_children_group.add_argument('-ac', '--add_children', type=int,
                                                        help='ids of the cards to add', nargs='*')
        card_editing_parser_children_group.add_argument('-rc', '--remove_children', type=int,
                                                        help='ids of the cards to remove', nargs='*')
        card_editing_parser.add_argument("-e", "--expiration_date",
                                         help="The new Expiration Date - format YYYY-MM-DD,hh:mm",
                                         action=ValidateDateAction)
        card_editing_parser_plan = card_editing_parser.add_mutually_exclusive_group()
        cards_editing_plan_group = card_editing_parser.add_argument_group('plan',
                                                                          'Arguments to configure periodical task')
        cards_editing_plan_group.add_argument('-r',
                                              '--repeat',
                                              help="Creates repeated card according to interval. E.g. repeat '1 week'")
        cards_editing_plan_group.add_argument('-sa',
                                              '--start_repeat_at',
                                              help="Start date time for repeated card. E.g. --sa 'in 3 days'",
                                              action=ValidateStartAtUsageAction)
        card_editing_parser_plan.add_argument_group(cards_editing_plan_group)
        card_editing_parser_plan.add_argument('-dp', '--delete_plan', help='Delete periodical card plan',
                                              action='store_true')

        parser_delete_card = card_subparsers.add_parser('delete', description='Delete card', help='delete card')
        parser_delete_card.add_argument('id', type=int, help='the id of the card')

        parser_archive_card = card_subparsers.add_parser('archive', description='Archive card', help='archive card')
        parser_archive_card.add_argument('id', type=int, help='the id of the card')

        card_show_parser = card_subparsers.add_parser('show', description='Show card', help='show card')
        parser_show_card_group = card_show_parser.add_mutually_exclusive_group()
        parser_show_card_group.required = True
        parser_show_card_group.add_argument('-i', '--id', type=int, help='show card with the particular id')
        parser_show_card_group.add_argument('-n', '--name', help='show card with the particular name')
        parser_show_card_group.add_argument('-c', '--created', help='show created cards by this user',
                                            action='store_true')
        parser_show_card_group.add_argument('-as', '--assigned', help='show assigned cards', action='store_true')
        parser_show_card_group.add_argument('-ar', '--archived', help='show archived cards', action='store_true')
        parser_show_card_group.add_argument('-cr', '--can_read', help='show cards that user can read',
                                            action='store_true')
        parser_show_card_group.add_argument('-cw', '--can_write', help='show cards that user can write',
                                            action='store_true')

        card_assign_parser = card_subparsers.add_parser('assign', description='Assign card', help='assign card')
        card_assign_parser.add_argument('-cid', '--card_id', type=int,
                                        help='identifier of the task to assign').required = True
        card_assign_parser.add_argument('-uid', '--user_id', type=int,
                                        help='identifier of the user who this card would be assigned').required = True

        parser_access_card = card_subparsers.add_parser('access',
                                                        description='Configure access to card',
                                                        help='configure access to card')
        parser_access_card.add_argument('-cid', '--card_id', help='the id of the card').required = True
        parser_access_card.add_argument('-uid', '--user_id', help='the id of the user').required = True
        parser_access_card.add_argument('mode', metavar="\033[4mmode\033[0m", help='access mode (+rw, ~rw)',
                                        action=ValidateAccessModeAction)

    def _add_tag_parser(self):
        tag_parser = self.object_subparsers.add_parser('tag',
                                                       description='Operate tags. Tags are used to group tasks even '
                                                                   'from different lists',
                                                       help='Operate tags. Tags are used to group tasks even '
                                                            'from different lists')
        tag_subparsers = tag_parser.add_subparsers(dest='command',
                                                   metavar="<command>",
                                                   title="commands that applicable to tags")
        tag_subparsers.required = True

        parser_show_tag = tag_subparsers.add_parser('show',
                                                    description='Show tags', help='show tags')
        parser_show_tag_group = parser_show_tag.add_mutually_exclusive_group()
        parser_show_tag_group.required = True

        parser_show_tag_group.add_argument('-a', '--all', help='show all tags', action='store_true')
        parser_show_tag_group.add_argument('-i', '--id', type=int, help='show cards with this TagID')
        parser_show_tag_group.add_argument('-n', '--name', help='show cards with this tag name')

        parser_add_tag = tag_subparsers.add_parser('add', description='Add tag', help='add tag')
        parser_add_tag.add_argument('name', help='name of the tag')

        parser_edit_tag = tag_subparsers.add_parser('edit', description='Edit tag', help='edit tag')
        parser_edit_tag.add_argument('id', help='the id of the tag to edit')
        parser_edit_tag.add_argument('-n', '--name', help='the new name of the tag')

        parser_delete_tag = tag_subparsers.add_parser('delete', description='Delete tag', help='delete tag')
        parser_delete_tag.add_argument('id', type=int, help='the id of the tag')

    def _add_user_parser(self):
        user_parser = self.object_subparsers.add_parser('user',
                                                        description="Operate users. Users may own and have different "
                                                                    "access to cards, lists, etc.",
                                                        help="Operate users. Users may own and have different "
                                                             "access to cards, lists, etc."
                                                        )
        user_subparsers = user_parser.add_subparsers(dest='command',
                                                     metavar="<command>",
                                                     title="commands that applicable to users")
        user_subparsers.required = True

        user_subparsers.add_parser('current', description='Show current user', help='show current user')

        parser_add_user = user_subparsers.add_parser('add', description='Add user', help='add user')
        parser_add_user.add_argument('username', help='name of the user')

        parser_login_user = user_subparsers.add_parser('login',
                                                       description='Login with username or id',
                                                       help='login with username or id')

        parser_login_user_group = parser_login_user.add_mutually_exclusive_group()
        parser_login_user_group.required = True

        parser_login_user_group.add_argument('-i', '--id', type=int, help='id of the user')
        parser_login_user_group.add_argument('-n', '--username', help='name of the user')

        user_subparsers.add_parser('logout',
                                   description='Logout from current user',
                                   help='logout from current user')

        user_subparsers.add_parser('all', description='Show all users', help='show all users')

    def _add_list_parser(self):
        list_parser = self.object_subparsers.add_parser('list',
                                                        description='Operate list. Lists contain cards',
                                                        help='Operate list. Lists contain cards')
        list_subparsers = list_parser.add_subparsers(dest='command',
                                                     metavar="<command>",
                                                     title="commands that applicable to lists")
        list_subparsers.required = True

        parser_show_list = list_subparsers.add_parser('show',
                                                      description='Show lists', help='show lists')
        parser_show_list_group = parser_show_list.add_mutually_exclusive_group()
        parser_show_list_group.required = True

        parser_show_list_group.add_argument('-a', '--all', help='show all lists in current board',
                                            action='store_true')
        parser_show_list_group.add_argument('-i', '--id', type=int, help='show lists with the particular id')
        parser_show_list_group.add_argument('-n', '--name', help='show lists with the particular name')

        parser_add_list = list_subparsers.add_parser('add', description='Add list', help='add list')
        parser_add_list.add_argument('name', help='name of the list')

        parser_edit_list = list_subparsers.add_parser('edit', description='Edit list', help='edit list')
        parser_edit_list.add_argument('id', help='the id of the list to edit')
        parser_edit_list.add_argument('-n', '--name', help='the new name of the list')

        parser_delete_list = list_subparsers.add_parser('delete', description='Delete list', help='delete list')
        parser_delete_list.add_argument('id', type=int, help='the id of the list')

        parser_access_list = list_subparsers.add_parser('access',
                                                        description='Configure access to list',
                                                        help='configure access to list')
        parser_access_list.add_argument('-lid', '--list_id', help='the id of the list').required = True
        parser_access_list.add_argument('-uid', '--user_id', help='the id of the user').required = True
        parser_access_list.add_argument('mode', metavar="\033[4mmode\033[0m", help='access mode (+rw, ~rw)',
                                        action=ValidateAccessModeAction)

    def _add_board_parser(self):
        board_parser = self.object_subparsers.add_parser('board',
                                                         description='Operate boards. Boards contain lists of cards',
                                                         help='Operate boards. Boards contain lists of cards')
        board_subparsers = board_parser.add_subparsers(dest='command',
                                                       metavar="<command>",
                                                       title="commands that applicable to boards")
        board_subparsers.required = True

        parser_show_board = board_subparsers.add_parser('show',
                                                        description='Show boards', help='show boards')
        parser_show_board_group = parser_show_board.add_mutually_exclusive_group()
        parser_show_board_group.required = True

        parser_show_board_group.add_argument('-c', '--current', help='show current board', action='store_true')
        parser_show_board_group.add_argument('-a', '--all', help='show all boards', action='store_true')
        parser_show_board_group.add_argument('-i', '--id', type=int, help='show board with the particular id')
        parser_show_board_group.add_argument('-n', '--name', help='show board with the particular name')

        parser_add_board = board_subparsers.add_parser('add', description='Add board', help='add board')
        parser_add_board.add_argument('name', help='name of the board')

        parser_edit_board = board_subparsers.add_parser('edit', description='Edit board', help='edit board')
        parser_edit_board.add_argument('id', help='the id of the board to edit')
        parser_edit_board.add_argument('-n', '--name', help='the new name of the board')

        parser_delete_board = board_subparsers.add_parser('delete', description='Delete board', help='delete board')
        parser_delete_board.add_argument('id', type=int, help='the id of the board')

        parser_delete_board = board_subparsers.add_parser('switch',
                                                          description='Switch to board', help='switch to board')
        parser_delete_board.add_argument('id', type=int, help='the id of the board')

        parser_access_board = board_subparsers.add_parser('access',
                                                          description='Configure access to board',
                                                          help='configure access to board')
        parser_access_board.add_argument('-bid', '--board_id', help='the id of the board').required = True
        parser_access_board.add_argument('-uid', '--user_id', help='the id of the user').required = True
        parser_access_board.add_argument('mode', metavar="\033[4mmode\033[0m", help='access mode (+rw, ~rw)',
                                         action=ValidateAccessModeAction)
