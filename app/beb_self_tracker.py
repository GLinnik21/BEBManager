import argparse
from datetime import datetime


def validate_date(s):
    try:
        return datetime.strptime(s, '%Y-%m-%d,%H:%M')
    except ValueError:
        msg = "Not valid date: '{}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


class CLIParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='BEBSelf issues tracker')
        self.subparsers = self.parser.add_subparsers(description='Objects to operate', dest='object')

        self._add_card_parser()
        self._add_list_parser()

    def parse(self, args=None):
        return self.parser.parse_args(args)

    def _add_card_parser(self):
        card_parser = self.subparsers.add_parser('card', description='Operations with card entities')
        card_subparser = card_parser.add_subparsers(dest='action')

        card_display_parser = card_subparser.add_parser('display', description='Display card')
        card_display_group = card_display_parser.add_mutually_exclusive_group()
        card_display_group.add_argument('-i', '--id', help='unique id of card')
        card_display_group.add_argument('-n', '--name', help='name of card (if not unique, all variants with ids '
                                                             'would be displayed)')
        card_display_parser.add_argument('-v', '--verbose', help='output details', action='store_true')

        card_deletion_parser = card_subparser.add_parser('delete', description='Delete card')
        card_deletion_group = card_deletion_parser.add_mutually_exclusive_group()
        card_deletion_group.add_argument('-i', '--id', help='unique id of card')
        card_deletion_group.add_argument('-n', '--name', help='name of card (if not unique, all variants with ids '
                                                              'would be displayed)')

        cards_creation_parser = card_subparser.add_parser('create', description='Create card')
        cards_creation_parser.add_argument('list_id', help='unique id of list where the card would be stored')
        cards_creation_parser.add_argument('name', help='name of the new card')
        cards_creation_parser.add_argument('-d', '--description', help='description of the task in the card')
        cards_creation_parser.add_argument('-p', '--priority', choices=['low', 'medium', 'high'], default='medium',
                                           help='priority of the card (default is "medium")')
        cards_creation_parser.add_argument("-e", "--expiration_date",
                                           help="The Expiration Date - format YYYY-MM-DD,hh:mm",
                                           type=validate_date)

        card_editing_parser = card_subparser.add_parser('edit', description='Change card')
        card_editing_parser.add_argument('-n', '--name')
        card_editing_parser.add_argument('-d', '--description')
        card_editing_parser.add_argument('-p', '--priority', choices=['low', 'medium', 'high'], default='medium',
                                         help='priority of the card (default is "medium")')
        card_editing_parser.add_argument("-e", "--expiration_date",
                                         help="The Expiration Date - format YYYY-MM-DD,hh:mm",
                                         type=validate_date)
        card_editing_parser.add_argument('task_id')

    def _add_list_parser(self):
        list_parser = self.subparsers.add_parser('list', description='Operations with card entities')
        card_subparser = list_parser.add_subparsers(dest='action')

        card_display_parser = card_subparser.add_parser('display', description='Display card')
        card_display_group = card_display_parser.add_mutually_exclusive_group()
        card_display_group.add_argument('-i', '--id', help='unique id of card')
        card_display_group.add_argument('-n', '--name', help='name of card (if not unique, all variants with ids '
                                                             'would be displayed)')
        card_display_parser.add_argument('-v', '--verbose', help='output details', action='store_true')

        card_deletion_parser = card_subparser.add_parser('delete', description='Delete card')
        card_deletion_group = card_deletion_parser.add_mutually_exclusive_group()
        card_deletion_group.add_argument('-i', '--id', help='unique id of card')
        card_deletion_group.add_argument('-n', '--name', help='name of card (if not unique, all variants with ids '
                                                              'would be displayed)')

        cards_creation_parser = card_subparser.add_parser('create', description='Create card')
        cards_creation_parser.add_argument('list_id', help='unique id of list where the card would be stored')
        cards_creation_parser.add_argument('name', help='name of the new card')
        cards_creation_parser.add_argument('-d', '--description', help='description of the task in the card')
        cards_creation_parser.add_argument('-p', '--priority', choices=['low', 'medium', 'high'], default='medium',
                                           help='priority of the card (default is "medium")')
        cards_creation_parser.add_argument("-e", "--expiration_date",
                                           help="The Expiration Date - format YYYY-MM-DD,hh:mm",
                                           type=validate_date)

        card_editing_parser = card_subparser.add_parser('edit', description='Change card')
        card_editing_parser.add_argument('-n', '--name')
        card_editing_parser.add_argument('-d', '--description')
        card_editing_parser.add_argument('-p', '--priority', choices=['low', 'medium', 'high'], default='medium',
                                         help='priority of the card (default is "medium")')
        card_editing_parser.add_argument("-e", "--expiration_date",
                                         help="The Expiration Date - format YYYY-MM-DD,hh:mm",
                                         type=validate_date)
        card_editing_parser.add_argument('task_id')


def main():
    CLIParser().parse('card create Hello 123 -e 2017-06-01,21:10'.split())


if __name__ == '__main__':
    main()
