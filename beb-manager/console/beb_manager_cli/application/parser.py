import argparse
from datetime import datetime


class ValidateDateAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        try:
            datetime.strptime(values, '%Y-%m-%d,%H:%M')
            namespace.EXPIRATION_DATE = values
        except ValueError:
            try:
                datetime.strptime(values, '%Y-%m-%d')
                namespace.EXPIRATION_DATE = values + ",9:00"
            except ValueError:
                parser.error("Not valid date: '{}'.".format(values))


class ValidateStartAtUsageAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if namespace.repeat is None:
            parser.error("[-sa START_REPEAT_AT] should be used only with [-r REPEAT]")
        else:
            namespace.start_repeat_at = values


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

    # Available objects are:
    #    list      Operate lists. Lists contain cards.
    #    tag

    def _add_all_parsers(self):
        self._add_card_parser()
        self._add_user_parser()
        self._add_board_parser()

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

        cards_creation_parser = card_subparsers.add_parser('add', description='Add card', help='Add card')
        cards_creation_list_group = cards_creation_parser.add_mutually_exclusive_group()
        cards_creation_list_group.required = True

        cards_creation_parser.add_argument('name', help='name of the new card')
        cards_creation_list_group.add_argument('-lid', '--list_id',
                                               help='unique id of list where the card would be stored')
        cards_creation_list_group.add_argument('-ln', '--list_name',
                                               help='name of list where the card would be stored')

        cards_creation_parser.add_argument('-d', '--description', help='description of the task in the card')
        cards_creation_parser.add_argument('-p', '--priority', choices=['low', 'medium', 'high'], default='medium',
                                           help='priority of the card (default is "medium")')
        cards_creation_parser.add_argument('-t', '--tags', help='name of the tags to add')
        cards_creation_parser.add_argument("-e", "--expiration_date",
                                           help="The Expiration Date - format YYYY-MM-DD,hh:mm",
                                           action=ValidateDateAction)
        cards_creation_plan_group = cards_creation_parser.add_argument_group('plan',
                                                                             'Arguments to configure periodical task')
        cards_creation_plan_group.required = False
        cards_creation_plan_group.add_argument('-r',
                                               '--repeat',
                                               help="Creates repeated card according to interval. E.g. repeat 'every "
                                                    "1 week'")
        cards_creation_plan_group.add_argument('-sa',
                                               '--start_repeat_at',
                                               help="Start date time for repeated card. E.g. --sa 'in 3 days'",
                                               action=ValidateStartAtUsageAction)

        card_editing_parser = card_subparsers.add_parser('edit', description='Change card', help='Change card')
        cards_editing_list_group = card_editing_parser.add_mutually_exclusive_group()
        cards_editing_list_group.required = True

        card_editing_parser.add_argument('card_id', help='unique identifier of the card that should be edited')
        cards_editing_list_group.add_argument('-lid', '--list_id',
                                              help='unique id of list where the card would be stored')
        cards_editing_list_group.add_argument('-ln', '--list_name',
                                              help='name of list where the card would be stored')
        card_editing_parser.add_argument('-n', '--name')

        card_editing_parser.add_argument('-d', '--description', help='description of the task in the card')
        card_editing_parser.add_argument('-p', '--priority', choices=['low', 'medium', 'high'],
                                         help='priority of the card')
        card_editing_parser_tag_group = card_editing_parser.add_mutually_exclusive_group()
        card_editing_parser_tag_group.add_argument('-at', '--add_tags', help='name of the tags to add')
        card_editing_parser_tag_group.add_argument('-rt', '--remove_tags', help='name of the tags to remove')
        card_editing_parser.add_argument("-e", "--expiration_date",
                                         help="The Expiration Date - format YYYY-MM-DD,hh:mm",
                                         action=ValidateDateAction)
        card_editing_parser_plan = card_editing_parser.add_mutually_exclusive_group()
        cards_editing_plan_group = card_editing_parser.add_argument_group('plan',
                                                                          'Arguments to configure periodical task')
        cards_editing_plan_group.add_argument('-r',
                                              '--repeat',
                                              help="Creates repeated card according to interval. E.g. repeat 'every "
                                                   "1 week'")
        cards_editing_plan_group.add_argument('-sa',
                                              '--start_repeat_at',
                                              help="Start date time for repeated card. E.g. --sa 'in 3 days'",
                                              action=ValidateStartAtUsageAction)
        card_editing_parser_plan.add_argument_group(cards_editing_plan_group)
        card_editing_parser_plan.add_argument('-dp', '--delete_plan', help='Delete periodical card plan',
                                              action='store_true')

        card_display_parser = card_subparsers.add_parser('display', description='Display card', help='display card')
        parser_display_card_group = card_display_parser.add_mutually_exclusive_group()
        parser_display_card_group.required = True
        parser_display_card_group.add_argument('-i', '--id', type=int, help='display card with the particular id')
        parser_display_card_group.add_argument('-n', '--name', help='display card with the particular name')
        parser_display_card_group.add_argument('-c', '--created', help='display created cards by this user')
        parser_display_card_group.add_argument('-as', '--assigned', help='display assigned cards')
        parser_display_card_group.add_argument('-ar', '--archived', help='display archived cards')
        parser_display_card_group.add_argument('-cr', '--can_read', help='display cards that user can read')
        parser_display_card_group.add_argument('-cw', '--can_write', help='display cards that user can write')

        card_assign_parser = card_subparsers.add_parser('assign', description='Assign card', help='assign card')
        card_assign_parser.add_argument('-cid', '--card_id', help='identifier of the task to assign').required = True
        card_assign_parser.add_argument('-uid', '--user_id',
                                        help='identifier of the user who this card would be assigned').required = True

        parser_access_card = card_subparsers.add_parser('access',
                                                        description='Configure access to card',
                                                        help='configure access to card')
        parser_access_card.add_argument('-cid', '--card_id', help='the id of the card').required = True
        parser_access_card.add_argument('-uid', '--user_id', help='the id of the user').required = True
        parser_access_card.add_argument('mode', metavar="\033[4mmode\033[0m", help='access mode (+rw, ~rw)')

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

        user_subparsers.add_parser('current', description='Display current user', help='display current user')

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

        user_subparsers.add_parser('all', description='Display all users', help='display all users')

    def _add_board_parser(self):
        board_parser = self.object_subparsers.add_parser('board',
                                                         description='Operate boards. Boards contain lists of cards',
                                                         help='Operate boards. Boards contain lists of cards')
        board_subparsers = board_parser.add_subparsers(dest='command',
                                                       metavar="<command>",
                                                       title="commands that applicable to boards")
        board_subparsers.required = True

        parser_display_board = board_subparsers.add_parser('display',
                                                           description='Display boards', help='display boards')
        parser_display_board_group = parser_display_board.add_mutually_exclusive_group()
        parser_display_board_group.required = True

        parser_display_board_group.add_argument('-c', '--current', help='display current board', action='store_true')
        parser_display_board_group.add_argument('-a', '--all', help='display all boards', action='store_true')
        parser_display_board_group.add_argument('-i', '--id', type=int, help='display board with the particular id')
        parser_display_board_group.add_argument('-n', '--name', help='display board with the particular name')

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
        parser_access_board.add_argument('mode', metavar="\033[4mmode\033[0m", help='access mode (+rw, ~rw)')
