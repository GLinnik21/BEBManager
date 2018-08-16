import argparse
import sys
from datetime import datetime


def validate_date(s):
    try:
        return datetime.strptime(s, '%Y-%m-%d,%H:%M')
    except ValueError:
        msg = "Not valid date: '{}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


class CLIParser:

    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Achieve your goals with BebSelf issues tracker')
        self.object_subparsers = self.parser.add_subparsers(dest='object',
                                                            metavar="<object>",
                                                            title="available objects are")
        self.object_subparsers.required = True

        self._add_all_parsers()

    def _add_all_parsers(self):
        self._add_card_parser()

    def parse(self):
        args = self.parser.parse_args()
        return args

# Available objects are:
#    board     Operate boards. Boards contain lists of cards
#    list      Operate lists. Lists contain cards.
#    card      Operate cards. Cards are the basic structure that's meant to represent one task
#    user      Operate users. Users may own and have different access to cards, lists, etc.

    def _add_card_parser(self):
        card_parser = self.object_subparsers.add_parser('card',
                                                        description="Operate cards. Cards are the basic structure "
                                                                    "that's meant to represent one task",
                                                        help="Operate cards. Cards are the basic structure "
                                                                    "that's meant to represent one task")
        card_subparser = card_parser.add_subparsers(dest='command',
                                                    metavar="<command>",
                                                    title="commands that applicable to cards")
        card_subparser.required = True

        card_display_parser = card_subparser.add_parser('display', description='Display card', help='Display card')
        card_display_group = card_display_parser.add_mutually_exclusive_group()
        card_display_group.required = True

        card_display_group.add_argument('-i', '--id', help='unique id of card')
        card_display_group.add_argument('-n', '--name', help='name of card (if not unique, all variants with ids '
                                                             'would be displayed)')
        card_display_parser.add_argument('-v', '--verbose', help='output details', action='store_true')

        card_deletion_parser = card_subparser.add_parser('delete', description='Delete card')
        card_deletion_group = card_deletion_parser.add_mutually_exclusive_group()
        card_deletion_group.add_argument('-i', '--id', help='unique id of card')
        card_deletion_group.add_argument('-n', '--name', help='name of card (if not unique, all variants with ids '
                                                              'would be displayed)')

        cards_creation_parser = card_subparser.add_parser('create', description='Create card', help='Create card')
        cards_creation_parser.add_argument('list_id', help='unique id of list where the card would be stored')
        cards_creation_parser.add_argument('name', help='name of the new card')
        cards_creation_parser.add_argument('-d', '--description', help='description of the task in the card')
        cards_creation_parser.add_argument('-p', '--priority', choices=['low', 'medium', 'high'], default='medium',
                                           help='priority of the card (default is "medium")')
        cards_creation_parser.add_argument("-e", "--expiration_date",
                                           help="The Expiration Date - format YYYY-MM-DD,hh:mm",
                                           type=validate_date)

        card_editing_parser = card_subparser.add_parser('edit', description='Change card', help='Change card')
        card_editing_parser.add_argument('-n', '--name')
        card_editing_parser.add_argument('-d', '--description')
        card_editing_parser.add_argument('-p', '--priority', choices=['low', 'medium', 'high'], default='medium',
                                         help='priority of the card (default is "medium")')
        card_editing_parser.add_argument("-e", "--expiration_date",
                                         help="The Expiration Date - format YYYY-MM-DD,hh:mm",
                                         type=validate_date)
        card_editing_parser.add_argument('card_id')


if __name__ == '__main__':
    sys.argv = "beb -h".split()
    CLIParser().parse()
