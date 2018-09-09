import random
import sys
from datetime import datetime
from typing import List, Optional

import dateparser

import beb_lib.model.exceptions as beb_exceptions
import beb_lib.logger as beb_logger
from beb_lib.domain_entities.board import Board
from beb_lib.domain_entities.card import Card
from beb_lib.domain_entities.card_list import CardsList
from beb_lib.domain_entities.supporting import AccessType, Priority
from beb_lib.model.model import Model
from beb_lib.provider_interfaces import RequestType

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


def check_board(func):
    def wrapper(self, *args, **kwargs):
        if self.working_board_manager.get_current_board_id() is None:
            print('Switch to board first!')
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
        beb_logger.init_logging(config.LOG_LEVEL, config.LOG_FILE, config.LOG_FORMAT, config.LOG_DATEFMT)
        self.lib_model = Model(config.LIB_DATABASE)
        self.lib_model.trigger_card_plan_creation()
        self.user_provider = UserProvider(config.APP_DATABASE)
        self.user_provider.open()
        self.authorization_manager = AuthorizationManager(config.CONFIG_FILE)
        self.working_board_manager = WorkingBoardManager(config.CONFIG_FILE)

    def get_all_users(self) -> List[UserInstance]:
        request = UserDataRequest(request_id=random.randrange(1000000),
                                  id=None,
                                  name=None,
                                  request_type=RequestType.READ)
        result, error = self.user_provider.execute(request)
        users = sorted(result.users, key=lambda user: user.unique_id)
        return users

    def get_user(self, user_id: Optional[int], name: Optional[str]) -> Optional[UserInstance]:
        request = UserDataRequest(request_id=random.randrange(1000000),
                                  id=user_id,
                                  name=name,
                                  request_type=RequestType.READ)
        result, error = self.user_provider.execute(request)

        if error is not None:
            if error.code == UserProviderErrorCodes.USER_DOES_NOT_EXIST:
                return None
            print("Database error: {}".format(error.description), file=sys.stderr)
            quit(error.code)

        if not result.users:
            return None
        else:
            return result.users[0]

    def add_user(self, name: str) -> None:
        request = UserDataRequest(request_id=random.randrange(1000000),
                                  id=None,
                                  name=name,
                                  request_type=RequestType.READ)
        result, error = self.user_provider.execute(request)

        if result.users:
            print("This username have been already taken!", file=sys.stderr)
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
            print("User with provided credentials was not found", file=sys.stderr)
            quit(1)

        self.authorization_manager.login_user(user.unique_id)
        print("Successfully logged in as {}".format(user.name))

    def print_all_users(self) -> None:
        users = self.get_all_users()
        if users:
            self._print_users(users)
        else:
            print('There are no users')
            quit()

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
        text = "CardID: {}   Name: {}".format(card.unique_id, card.name)
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
            except beb_exceptions.TagDoesNotExistError:
                pass

        text += "\nCreated: {}".format(card.created.strftime("%c"))
        text += "\nModified: {}".format(card.last_modified.strftime("%c"))
        if card.plan is not None:
            plan_text = "Periodical task plan"
            plan_text += "\nRepeats every: {}".format(card.plan.interval)
            plan_text += "\nLast created at: {}".format(card.plan.last_created_at.strftime("%c"))
            text += ("\n" + bordered(plan_text))
        print(bordered(text))

    def _create_plan(self, repeat: str, start_at: str, card_id: int):
        parsed_time = dateparser.parse(repeat)
        if parsed_time is None:
            print("Error. Repeat time is incorrect", file=sys.stderr)
            quit(1)
        else:
            interval = datetime.now() - parsed_time
            last_created_at = datetime.now() - interval
            if interval.total_seconds() < 300:
                print("Error. Task's interval is incorrect", file=sys.stderr)
            else:
                if start_at is not None:
                    start_date = dateparser.parse(start_at)
                    if start_date is not None:
                        time_delta = interval - (start_date - datetime.now())
                        last_created_at = datetime.now() - time_delta
            self.lib_model.plan_write(card_id,
                                      self.authorization_manager.get_current_user_id(),
                                      interval,
                                      last_created_at)

    def _get_board(self, board_id: Optional[int], board_name: Optional[str]) -> List[Board]:
        try:
            return self.lib_model.board_read(board_id, board_name, self.authorization_manager.get_current_user_id())
        except beb_exceptions.Error as error:
            print(error, file=sys.stderr)
            quit(1)

    def _add_rights(self, permissions: str, user_id: int, obj_id: int, object_type: type):
        access_type = AccessType.NONE

        if 'w' in permissions:
            access_type |= AccessType.WRITE
        if 'r' in permissions:
            access_type |= AccessType.READ

        self.lib_model.add_right(obj_id, object_type, user_id, access_type)

    def _remove_rights(self, permissions: str, user_id: int, obj_id: int, object_type: type):
        access_type = AccessType.NONE

        if 'w' in permissions:
            access_type |= AccessType.WRITE
        if 'r' in permissions:
            access_type |= AccessType.READ

        self.lib_model.remove_right(obj_id, object_type, user_id, access_type)

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
        boards = self._get_board(board_id, board_name)

        if len(boards) > 1:
            print("There are several board with this name:")
        for board in boards:
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
        except beb_exceptions.Error as error:
            print(error, file=sys.stderr)
            quit(1)

    @check_authorization
    def add_board(self, board_name: str) -> None:
        try:
            self.lib_model.board_write(board_name=board_name,
                                       request_user_id=self.authorization_manager.get_current_user_id())
        except beb_exceptions.Error as error:
            print(error, file=sys.stderr)
            quit(1)

    @check_authorization
    def delete_board(self, board_id: int) -> None:
        try:
            self.lib_model.board_delete(board_id, None, self.authorization_manager.get_current_user_id())
        except beb_exceptions.Error as error:
            print(error, file=sys.stderr)
            quit(1)

    @check_authorization
    def edit_board(self, board_id: int, new_name: str) -> None:
        board = self._get_board(board_id, None)[0]
        try:
            self.lib_model.board_write(board.unique_id, new_name, self.authorization_manager.get_current_user_id())
        except beb_exceptions.Error as error:
            print(error, file=sys.stderr)
            quit(1)

    @check_authorization
    def switch_board(self, board_id: int):
        try:
            self.lib_model.board_read(board_id, None, self.authorization_manager.get_current_user_id())
        except beb_exceptions.Error as error:
            print(error, file=sys.stderr)
            quit(1)

        self.working_board_manager.switch_to_board(board_id)

    def add_board_rights(self, param: str, user_id: int, board_id: int):
        self._add_rights(param, user_id, board_id, Board)

    def remove_board_rights(self, param: str, user_id: int, board_id: int):
        self._remove_rights(param, user_id, board_id, Board)

    @check_board
    def print_all_lists(self):
        self.print_current_board()

    @check_board
    @check_authorization
    def print_list(self, list_id: int, list_name: str):
        card_lists = self.lib_model.list_read(None, list_id, list_name,
                                              request_user_id=self.authorization_manager.get_current_user_id())
        if len(card_lists) > 1:
            print("There are several lists with this name:")
        for card_list in card_lists:
            print("ListID: {}   Name: {}".format(card_list.unique_id, card_list.name))
            try:
                cards = self.lib_model.card_read(list_id,
                                                 request_user_id=self.authorization_manager.get_current_user_id())

                if len(cards) > 0:
                    for card in cards:
                        self._print_card(card)
                else:
                    print("There are no cards in this list")
            except beb_exceptions.Error as error:
                print(error, file=sys.stderr)
                quit(1)

    @check_board
    @check_authorization
    def add_list(self, name):
        try:
            self.lib_model.list_write(board_id=self.working_board_manager.get_current_board_id(),
                                      list_name=name,
                                      request_user_id=self.authorization_manager.get_current_user_id())
        except beb_exceptions.Error as error:
            print(error, file=sys.stderr)
            quit(1)

    @check_authorization
    @check_board
    def edit_list(self, list_id: int, new_name: str) -> None:
        try:
            self.lib_model.list_read(board_id=self.working_board_manager.get_current_board_id(),
                                     list_id=list_id,
                                     request_user_id=self.authorization_manager.get_current_user_id())

            self.lib_model.list_write(self.working_board_manager.get_current_board_id(), list_id, new_name,
                                      self.authorization_manager.get_current_user_id())
        except beb_exceptions.Error as error:
            print(error, file=sys.stderr)
            quit(1)

    @check_authorization
    @check_board
    def delete_list(self, list_id: int):
        try:
            self.lib_model.list_delete(list_id, None, self.authorization_manager.get_current_user_id())
        except beb_exceptions.Error as error:
            print(error, file=sys.stderr)
            quit(1)

    def add_list_rights(self, param: str, user_id: int, list_id: int):
        self._add_rights(param, user_id, list_id, CardsList)

    def remove_list_rights(self, param: str, user_id: int, list_id: int):
        self._remove_rights(param, user_id, list_id, CardsList)

    @check_authorization
    def print_card(self, card_id: Optional[int], card_name: Optional[str]):
        try:
            cards = self.lib_model.card_read(None, card_id, card_name,
                                             self.authorization_manager.get_current_user_id())
            if len(cards) > 1:
                print("There are several cards with this name:")
            for card in cards:
                self._print_card(card)
        except beb_exceptions.Error as error:
            print(error, file=sys.stderr)
            quit(1)

    @check_authorization
    def print_created(self):
        for card in self.lib_model.get_cards_owned_by_user(self.authorization_manager.get_current_user_id()):
            self._print_card(card)

    @check_authorization
    def print_assigned(self):
        for card in self.lib_model.get_cards_assigned_user(self.authorization_manager.get_current_user_id()):
            self._print_card(card)

    @check_authorization
    def print_archived(self):
        self.lib_model.get_archived_cards(self.authorization_manager.get_current_user_id())

    @check_authorization
    def print_readable_cards(self):
        cards = self.lib_model.get_readable_cards(self.authorization_manager.get_current_user_id())
        for card in cards:
            self._print_card(card)

    @check_authorization
    def print_writable_cards(self):
        cards = self.lib_model.get_writable_cards(self.authorization_manager.get_current_user_id())
        for card in cards:
            self._print_card(card)

    @check_authorization
    def add_card(self, name: str, list_id: int, list_name: str, description: str,
                 priority: str, tags: List[str], children: List[int], exp_date: str, repeat: str, start: str):
        try:
            card_lists = self.lib_model.list_read(self.working_board_manager.get_current_board_id(),
                                                  list_id,
                                                  list_name,
                                                  self.authorization_manager.get_current_user_id())

            card_list = None

            if len(card_lists) > 1:
                print("There are several lists with this name:")
                for card_list in card_lists:
                    print("ListID: {}".format(card_list.unique_id))
                print("Please, specify one of these ListIDs")
                quit()
            else:
                card_list = card_lists[0]

            tag_ids = None
            try:
                if tags is not None:
                    tag_ids = [self.lib_model.tag_read(tag_name=tag_name)[0].unique_id for tag_name in tags]
            except beb_exceptions.TagDoesNotExistError:
                print('One of the tags does not exist', file=sys.stderr)
                quit(1)

            if children is not None:
                try:
                    for child in children:
                        self.lib_model.card_read(None, child,
                                                 request_user_id=self.authorization_manager.get_current_user_id())
                except beb_exceptions.CardDoesNotExistError:
                    print('One of the children cards does not exist', file=sys.stderr)
                    quit(1)
                except beb_exceptions.AccessDeniedError:
                    print("You can't read one of the children cards", file=sys.stderr)
                    quit(1)

            card = Card(name=name,
                        description=description,
                        expiration_date=None if exp_date is None else datetime.strptime(exp_date, '%Y-%m-%d,%H:%M'),
                        priority=Priority[priority.upper()],
                        tags=tag_ids,
                        children=children)

            card = self.lib_model.card_write(card_list.unique_id, card,
                                             self.authorization_manager.get_current_user_id())

            if repeat is not None:
                self._create_plan(repeat, start, card.unique_id)

        except beb_exceptions.Error as error:
            print(error, file=sys.stderr)
            quit(1)

    @check_authorization
    def edit_card(self, card_id: int, name: str, list_id: int, list_name: str, description: str,
                  priority: str, add_tags: List[str], remove_tags: List[str], add_children: List[int],
                  remove_children: List[int], exp_date: str, delete_plan: bool, repeat: str, start: str):
        try:
            card_list = None

            if list_id is not None or list_name is not None:
                card_lists = self.lib_model.list_read(self.working_board_manager.get_current_board_id(),
                                                      list_id,
                                                      list_name,
                                                      self.authorization_manager.get_current_user_id())

                if len(card_lists) > 1:
                    print("There are several lists with this name:")
                    for card_list in card_lists:
                        print("ListID: {}".format(card_list.unique_id))
                    print("Please, specify one of these ListIDs")
                    quit()
                else:
                    card_list = card_lists[0].unique_id

            card = self.lib_model.card_read(None, card_id=card_id,
                                            request_user_id=self.authorization_manager.get_current_user_id())[0]

            try:
                if add_tags is not None:
                    card.tags.append([self.lib_model.tag_read(tag_name=tag_name)[0].unique_id for tag_name in add_tags])

                if remove_tags is not None:
                    tag_ids = [self.lib_model.tag_read(tag_name=tag_name)[0].unique_id for tag_name in remove_tags]
                    for tag in tag_ids:
                        card.tags.remove(tag)
            except beb_exceptions.TagDoesNotExistError:
                print('One of the tags does not exist', file=sys.stderr)
                quit(1)
            except ValueError:
                print('One of the tags is not in the card', file=sys.stderr)
                quit(1)

            try:
                if add_children is not None:
                    for child in add_children:
                        self.lib_model.card_read(None, child,
                                                 request_user_id=self.authorization_manager.get_current_user_id())
                        card.children.add(child)
                if remove_children is not None:
                    for child in remove_children:
                        card.children.remove(child)
            except beb_exceptions.CardDoesNotExistError:
                print('One of the children cards does not exist', file=sys.stderr)
                quit(1)
            except beb_exceptions.AccessDeniedError:
                print("You can't read one of the children cards", file=sys.stderr)
                quit(1)
            except ValueError:
                print('One of the cards is not a child of this card', file=sys.stderr)
                quit(1)

            if name is not None:
                card.name = name
            if description is not None:
                card.description = description
            if priority is not None:
                card.priority = Priority[priority.upper()]
            if exp_date is not None:
                card.expiration_date = exp_date

            self.lib_model.card_write(card_list, card, self.authorization_manager.get_current_user_id())

            if delete_plan:
                self.lib_model.plan_delete(card.unique_id, self.authorization_manager.get_current_user_id())
            elif repeat is not None:
                self._create_plan(repeat, start, card.unique_id)

        except beb_exceptions.Error as error:
            print(error, file=sys.stderr)
            quit(1)

    @check_authorization
    def delete_card(self, card_id: int):
        try:
            self.lib_model.card_delete(card_id=card_id,
                                       request_user_id=self.authorization_manager.get_current_user_id())
        except beb_exceptions.Error as error:
            print(error, file=sys.stderr)
            quit(1)

    @check_authorization
    def archive_card(self, card_id: int):
        try:
            self.lib_model.archive_card(card_id, request_user_id=self.authorization_manager.get_current_user_id())
        except beb_exceptions.Error as error:
            print(error, file=sys.stderr)
            quit(1)

    def add_card_rights(self, param: str, user_id: int, card_id: int):
        self._add_rights(param, user_id, card_id, Card)

    def remove_card_rights(self, param: str, user_id: int, card_id: int):
        self._remove_rights(param, user_id, card_id, Card)

    @check_authorization
    def assign_card(self, card_id: int, user_id: int):
        self.get_user(user_id, None)
        try:
            card = self.lib_model.card_read(None, card_id,
                                            request_user_id=self.authorization_manager.get_current_user_id())[0]
            card.assignee_id = user_id
            self.lib_model.card_write(None, card, request_user_id=self.authorization_manager.get_current_user_id())
        except beb_exceptions.Error as error:
            print(error, file=sys.stderr)
            quit(1)

    def add_tag(self, name: str):
        try:
            self.lib_model.tag_read(tag_name=name)
            print("Tag already exists!", file=sys.stderr)
            quit(1)
        except beb_exceptions.TagDoesNotExistError:
            pass
        except beb_exceptions.Error as error:
            print(error, file=sys.stderr)
            quit(1)

        self.lib_model.tag_write(tag_name=name)

    def edit_tag(self, tag_id: int, name: str):
        try:
            self.lib_model.tag_read(tag_id=tag_id)
            self.lib_model.tag_write(tag_id=tag_id, tag_name=name)
        except beb_exceptions.TagDoesNotExistError:
            print("This tag doesn't exist", file=sys.stderr)
            quit(1)
        except beb_exceptions.Error as error:
            print(error, file=sys.stderr)
            quit(1)

    def delete_tag(self, tag_id: int):
        try:
            self.lib_model.tag_delete(tag_id)
        except beb_exceptions.Error as error:
            print(error, file=sys.stderr)
            quit(1)

    def show_all_tags(self):
        tags = self.lib_model.tag_read()
        if tags:
            for tag in tags:
                print("TagID: {}    Name: {}".format(tag.unique_id, tag.name))
        else:
            print("There are no tags created")
            quit()

    @check_authorization
    def print_cards_by_tag(self, tag_id: int, tag_name: str):
        try:
            tag = self.lib_model.tag_read(tag_id, tag_name)[0]
            cards = self.lib_model.card_read(None, tag_id=tag.unique_id,
                                             request_user_id=self.authorization_manager.get_current_user_id())
            if cards:
                for card in cards:
                    self._print_card(card)
            else:
                print("There are no cards with this tag")
                quit()
        except beb_exceptions.Error as error:
            print(error, file=sys.stderr)
            quit(1)
