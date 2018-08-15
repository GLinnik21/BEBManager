import argparse
import sys


class CLIParser(object):

    def __init__(self):
        parser = argparse.ArgumentParser(description='Achieve your goals with BebSelf issues tracker',
                                     usage='''beb <command> [<args>]
                                     Available commands are:
                                     add     Add new entity to the issues tracker
                                     delete  Delete entity form the issues tracker
                                     change  Change entity form the issues tracker
                                     ''')
        parser.add_argument('command', help='Subcommand to run')

        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        getattr(self, args.command)()

    def add(self):
        parser = argparse.ArgumentParser(description='Add new entity to the issues tracker')
        # prefixing the argument with -- means it's optional
        parser.add_argument('--amend', action='store_true')
        # now that we're inside a subcommand, ignore the first
        # TWO argvs, ie the command (git) and the subcommand (commit)
        args = parser.parse_args(sys.argv[2:])
        print('Running git commit, amend=%s' % args.amend)

    def delete(self):
        parser = argparse.ArgumentParser(description='Delete entity form the issues tracker')
        # NOT prefixing the argument with -- means it's not optional
        parser.add_argument('repository')
        args = parser.parse_args(sys.argv[2:])
        print('Running git fetch, repository=%s' % args.repository)
