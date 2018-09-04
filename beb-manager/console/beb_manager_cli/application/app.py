import random
from typing import List, Optional

import beb_lib.model.exceptions as beb_lib_exceptions
from beb_lib.domain_entities.board import Board
from beb_lib.domain_entities.card import Card
from beb_lib.domain_entities.supporting import AccessType, Priority
from beb_lib.model.model import Model
from beb_lib.provider_interfaces import RequestType, BaseError

import beb_manager_cli.application.config as config
from beb_manager_cli.application.authorization_manager import AuthorizationManager
from beb_manager_cli.application.working_board_manager import WorkingBoardManager
from beb_manager_cli.storage.user import UserInstance
from beb_manager_cli.storage.user_provider import UserProvider, UserDataRequest, UserProviderErrorCodes


def check_authorization(func):
    def wrapper(self, *args, **kwargs):
        if self.authorization_manager.get_current_user_id() is None:
            print('Authorize first!')
            quit(1)
        else:
            return func(self, *args, **kwargs)

    return wrapper


def bordered(text):
    lines = text.splitlines()
    width = max(len(s) for s in lines)
    res = ['┌' + '─' * width + '┐']
    for s in lines:
        res.append('│' + (s + ' ' * width)[:width] + '│')
    res.append('└' + '─' * width + '┘')
    return '\n'.join(res)


class App:

    def __init__(self):
        self.lib_model = Model(config.LIB_DATABASE)
        self.user_provider = UserProvider(config.APP_DATABASE)
        self.user_provider.open()
        self.authorization_manager = AuthorizationManager(config.CONFIG_FILE)
        self.working_board_manager = WorkingBoardManager(config.CONFIG_FILE)

    def get_all_users(self) -> List[UserInstance]:
        request = UserDataRequest(request_id=random.randrange(1000000),
                                  id=None,
                                  name=None,
                                  request_type=RequestType.READ)
        result = self.user_provider.execute(request)[0]
        users = sorted(result.users, key=lambda user: user.unique_id)
        return users

    def get_user(self, user_id: Optional[int], name: Optional[str]) -> Optional[UserInstance]:
        request = UserDataRequest(request_id=random.randrange(1000000),
                                  id=user_id,
                                  name=name,
                                  request_type=RequestType.READ)
        result = self.user_provider.execute(request)

        error: Optional[BaseError] = result[1]

        if error is not None:
            if error.code == UserProviderErrorCodes.USER_DOES_NOT_EXIST:
                return None
            print("Database error: {}".format(result[1].description))
            quit(error.code)

        users: Optional[List[UserInstance]] = result[0].users
        if not users:
            return None
        else:
            return users[0]

    def add_user(self, name: str) -> None:
        request = UserDataRequest(request_id=random.randrange(1000000),
                                  id=None,
                                  name=name,
                                  request_type=RequestType.READ)
        result = self.user_provider.execute(request)

        if result[1] is not None:
            print(result[1].description)
            quit(1)

        if result[0].users:
            print("This username have been already taken!")
            quit(1)

        request = UserDataRequest(request_id=random.randrange(1000000),
                                  id=None,
                                  name=name,
                                  request_type=RequestType.WRITE)
        result = self.user_provider.execute(request)

        if result[1] is not None:
            print(result[1].description)
            quit(1)

    def logout_user(self):
        user_id = self.authorization_manager.get_current_user_id()

        if user_id is None:
            print("You were not logged in")
            quit()

        user = self.get_user(user_id, None)

        if user is not None:
            self.authorization_manager.logout_user()
            print("Successfully logged out from {}".format(user.name))
        else:
            print("You were not logged in")

    def login_user(self, name: str, user_id: int) -> None:
        user = None

        if name is not None:
            user = self.get_user(None, name)
        elif user_id is not None:
            user = self.get_user(user_id, None)

        if user is None:
            print("User with provided credentials was not found")
            quit(1)

        self.authorization_manager.login_user(user.unique_id)
        print("Successfully logged in as {}".format(user.name))

    def print_all_users(self) -> None:
        users = self.get_all_users()
        self._print_users(users)

    @check_authorization
    def print_current_user(self) -> None:
        user_id = self.authorization_manager.get_current_user_id()

        user = self.get_user(user_id, None)

        self._print_users([user])

    @staticmethod
    def _print_users(users: List[UserInstance]) -> None:
        for user in users:
            print("UserID: {}   Name: {}".format(user.unique_id, user.name))

    def _print_card(self, card: Card):
        text = "CardID: {}   Name: {}".format(card.user_id, card.name)
        if card.description is not None:
            text += "\nDescription: {}".format(card.description)

        try:
            priority = Priority(card.priority).name
        except ValueError:
            priority = str(card.priority)

        text += ("\nPriority: " + priority)
        user = self.get_user(card.user_id, None)
        if user is not None:
            text += "\nOwner: {} aka {}".format(card.user_id, self.get_user(card.user_id, None).name)
        else:
            text += "\nOwner: {}".format(card.user_id)
        if card.assignee_id is not None:
            assignee = self.get_user(card.assignee_id, None)
            if assignee is not None:
                text += "\nAssignee: {} aka {}".format(card.assignee_id,
                                                       self.get_user(card.assignee_id, None).name)
            else:
                text += "\nAssignee: {}".format(card.assignee_id)

        if len(card.children) > 0:
            text += "\nChildren cards: {}".format(card.children)

        if len(card.tags) > 0:
            try:
                tags = [self.lib_model.tag_read(tag)[0].name for tag in card.tags]
                text += "\nTags: {}".format(tags)
            except beb_lib_exceptions.TagDoesNotExistError:
                pass

        text += "\nCreated: {}".format(card.created.strftime("%A %d. %B %Y"))
        text += "\nModified: {}".format(card.last_modified.strftime("%A %d. %B %Y"))
        if card.plan is not None:
            plan_text = "Periodical task plan"
            plan_text += "\nRepeats every: {}".format(card.plan.interval)
            plan_text += "\nLast created at: {}".format(card.plan.last_created_at.strftime("%A %d. %B %Y"))
            text += ("\n" + bordered(plan_text))
        print(bordered(text))

    @staticmethod
    def _print_boards(boards: List[Board]) -> None:
        for board in boards:
            print("BoardID: {}   Name: {}".format(board.unique_id, board.name))

    @check_authorization
    def print_current_board(self):
        board_id = self.working_board_manager.get_current_board_id()
        if board_id is None:
            print("You're not currently switched to any board")
            quit()
        else:
            self.print_board(board_id, None)

    @check_authorization
    def print_board(self, board_id: Optional[int], board_name: Optional[str]):
        board = self.get_board(board_id, board_name)
        App._print_boards([board])

        if len(board.lists) > 0:
            print("\nLists in this board:")
            card_lists = self.lib_model.list_read(board.unique_id,
                                                  request_user_id=self.authorization_manager.get_current_user_id())
            for card_list in card_lists:
                print("ListID: {}   Name: {}".format(card_list.unique_id, card_list.name))
        else:
            print("There are no lists in this board")

    @check_authorization
    def print_all_boards(self):
        try:
            boards = self.lib_model.board_read(request_user_id=self.authorization_manager.get_current_user_id())
            if len(boards) > 0:
                App._print_boards(boards)
            else:
                print("There are no boards created.")
                quit()
        except beb_lib_exceptions.Error as error:
            print(error)
            quit(1)

    @check_authorization
    def get_board(self, board_id: Optional[int], board_name: Optional[str]) -> Board:
        try:
            boards = self.lib_model.board_read(board_id, board_name, self.authorization_manager.get_current_user_id())
            return boards[0]
        except beb_lib_exceptions.Error as error:
            print(error)
            quit(1)

    @check_authorization
    def add_board(self, board_name: str) -> None:

        boards = None

        try:
            boards = self.lib_model.board_read(board_name=board_name,
                                               request_user_id=self.authorization_manager.get_current_user_id())

        except beb_lib_exceptions.AccessDeniedError:
            print("This user can't create board with such name")
            quit(1)
        except beb_lib_exceptions.BoardDoesNotExistError:
            pass
        except beb_lib_exceptions.Error as error:
            print(error)
            quit(1)

        if boards is not None:
            print("Board with this name already exists")
            quit(1)

        try:
            self.lib_model.board_write(board_name=board_name,
                                       request_user_id=self.authorization_manager.get_current_user_id())
        except beb_lib_exceptions.Error as error:
            print(error)
            quit(1)

    @check_authorization
    def delete_board(self, board_id: int) -> None:
        try:
            self.lib_model.board_delete(board_id, None, self.authorization_manager.get_current_user_id())
        except beb_lib_exceptions.Error as error:
            print(error)
            quit(1)

    @check_authorization
    def edit_board(self, board_id: int, new_name: str) -> None:
        board = self.get_board(board_id, None)
        try:
            self.lib_model.board_write(board.unique_id, new_name, self.authorization_manager.get_current_user_id())
        except beb_lib_exceptions.Error as error:
            print(error)
            quit(1)

    @check_authorization
    def switch_board(self, board_id: int):
        try:
            self.lib_model.board_read(board_id, None, self.authorization_manager.get_current_user_id())
        except beb_lib_exceptions.Error as error:
            print(error)
            quit(1)

        self.working_board_manager.switch_to_board(board_id)

    def add_rights(self, permissions: str, user_id: int, board_id: int):
        access_type = AccessType.NONE

        if 'w' in permissions:
            access_type |= AccessType.WRITE
        if 'r' in permissions:
            access_type |= AccessType.READ

        self.lib_model.add_right(board_id, Board, user_id, access_type)

    def remove_rights(self, permissions: str, user_id: int, board_id: int):
        access_type = AccessType.NONE

        if 'w' in permissions:
            access_type |= AccessType.WRITE
        if 'r' in permissions:
            access_type |= AccessType.READ

        self.lib_model.remove_right(board_id, Board, user_id, access_type)

    def print_all_lists(self):
        self.print_current_board()

    def print_list(self, list_id: int, list_name: str):
        card_list = self.lib_model.list_read(None, list_id, list_name,
                                             request_user_id=self.authorization_manager.get_current_user_id())[0]
        print("ListID: {}   Name: {}".format(card_list.unique_id, card_list.name))
        try:
            cards = self.lib_model.card_read(list_id, request_user_id=self.authorization_manager.get_current_user_id())

            if len(cards) > 0:
                for card in cards:
                    self._print_card(card)
            else:
                print("There are no cards in this list")
        except beb_lib_exceptions.Error as error:
            print(error)
            quit(1)
