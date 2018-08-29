import random
from typing import List, Optional

from beb_lib.storage.storage_provider import StorageProviderErrors

from application import config, AuthorizationManager, WorkingBoardManager
from beb_lib import (StorageProvider,
                     BoardDataRequest,
                     RequestType,
                     Model,
                     BaseError,
                     Board,
                     AddAccessRightRequest,
                     RemoveAccessRightRequest, AccessType)
from storage import (UserProvider,
                     UserDataRequest,
                     UserInstance)
from storage.user_provider import UserProviderErrorCodes


def check_authorization(func):
    def wrapper(self, *args, **kwargs):
        if self.authorization_manager.get_current_user_id() is None:
            print('Authorize first!')
            quit(1)
        else:
            func(self, *args, **kwargs)

    return wrapper


class App:

    def __init__(self):
        self.lib_model = Model(StorageProvider(config.LIB_DATABASE))
        self.user_provider = UserProvider(config.APP_DATABASE)
        self.user_provider.open()
        self.authorization_manager = AuthorizationManager(config.CONFIG_FILE)
        self.working_board_manager = WorkingBoardManager(config.CONFIG_FILE)

    def get_all_users(self) -> List[UserInstance]:
        request = UserDataRequest(request_id=random.randrange(1000000),
                                  id=None,
                                  name=None,
                                  request_type=RequestType.READ)
        result = self.user_provider.sync_execute(request)[0]
        users = sorted(result.users, key=lambda user: user.unique_id)
        return users

    def get_user(self, user_id: Optional[int], name: Optional[str]) -> Optional[UserInstance]:
        request = UserDataRequest(request_id=random.randrange(1000000),
                                  id=user_id,
                                  name=name,
                                  request_type=RequestType.READ)
        result = self.user_provider.sync_execute(request)

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
        result = self.user_provider.sync_execute(request)

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
        result = self.user_provider.sync_execute(request)

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
            App._print_boards([self.get_board(board_id, None)])

    @check_authorization
    def print_board(self, board_id: int, board_name: str):
        App._print_boards([self.get_board(board_id, board_name)])

    @check_authorization
    def print_all_boards(self):
        request = BoardDataRequest(request_id=random.randrange(1000000),
                                   request_user_id=self.authorization_manager.get_current_user_id(),
                                   id=None,
                                   name=None,
                                   request_type=RequestType.READ)
        result = self.lib_model.sync_execute(request)
        response, error = result

        if error is not None:
            print(error.description)
            quit(error.code)

        if len(response.boards) > 0:
            App._print_boards(response.boards)
        else:
            print("There are no boards created.")
            quit()

    def get_board(self, board_id: Optional[int], board_name: Optional[str]) -> Board:
        request = BoardDataRequest(request_id=random.randrange(1000000),
                                   request_user_id=self.authorization_manager.get_current_user_id(),
                                   id=board_id,
                                   name=board_name,
                                   request_type=RequestType.READ)
        response, error = self.lib_model.sync_execute(request)

        if error is not None:
            print(error.description)
            quit(error.code)

        return response.boards[0]

    @check_authorization
    def add_board(self, board_name: str) -> None:
        request = BoardDataRequest(request_id=random.randrange(1000000),
                                   request_user_id=self.authorization_manager.get_current_user_id(),
                                   id=None,
                                   name=board_name,
                                   request_type=RequestType.READ)
        response, error = self.lib_model.sync_execute(request)

        if response is not None:
            print("Board with this name already exists")
            quit(1)
        elif error is not None:
            if error.code == StorageProviderErrors.ACCESS_DENIED:
                print("This user can't create board with such name")
                quit(1)
            elif error.code == StorageProviderErrors.BOARD_DOES_NOT_EXIST:
                pass
            else:
                print(error.description)
                quit(error.code)

        request = BoardDataRequest(request_id=random.randrange(1000000),
                                   request_user_id=self.authorization_manager.get_current_user_id(),
                                   id=None,
                                   name=board_name,
                                   request_type=RequestType.WRITE)
        response, error = self.lib_model.sync_execute(request)

        if error is not None:
            print(error.description)
            quit(error.code)

    @check_authorization
    def delete_board(self, board_id: int) -> None:
        request = BoardDataRequest(request_id=random.randrange(1000000),
                                   request_user_id=self.authorization_manager.get_current_user_id(),
                                   id=board_id,
                                   name=None,
                                   request_type=RequestType.DELETE)
        response, error = self.lib_model.sync_execute(request)

        if error is not None:
            print(error.description)
            quit(error.code)

    @check_authorization
    def edit_board(self, board_id: int, new_name: str) -> None:
        board = self.get_board(board_id, None)

        request = BoardDataRequest(request_id=random.randrange(1000000),
                                   request_user_id=self.authorization_manager.get_current_user_id(),
                                   id=board.unique_id,
                                   name=new_name,
                                   request_type=RequestType.WRITE)

        response, error = self.lib_model.sync_execute(request)

        if error is not None:
            print(error.description)
            quit(error.code)

    @check_authorization
    def switch_board(self, board_id: int):
        request = BoardDataRequest(request_id=random.randrange(1000000),
                                   request_user_id=self.authorization_manager.get_current_user_id(),
                                   id=board_id,
                                   name=None,
                                   request_type=RequestType.READ)

        response, error = self.lib_model.sync_execute(request)

        if error is not None:
            print(error.description)
            quit(error.code)

        self.working_board_manager.switch_to_board(board_id)

    def add_rights(self, permissions: str, user_id: int, board_id: int):
        access_type = AccessType.NONE

        if 'w' in permissions:
            access_type |= AccessType.WRITE
        if 'r' in permissions:
            access_type |= AccessType.READ

        request = AddAccessRightRequest(request_id=random.randrange(1000000),
                                        request_type=None,
                                        object_id=board_id,
                                        object_type=Board,
                                        user_id=user_id,
                                        access_type=access_type)
        self.lib_model.sync_execute(request)

    def remove_rights(self, permissions: str, user_id: int, board_id: int):
        access_type = AccessType.NONE

        if 'w' in permissions:
            access_type |= AccessType.WRITE
        if 'r' in permissions:
            access_type |= AccessType.READ

        request = RemoveAccessRightRequest(request_id=random.randrange(1000000),
                                           request_type=None,
                                           object_id=board_id,
                                           object_type=Board,
                                           user_id=user_id,
                                           access_type=access_type)
        self.lib_model.sync_execute(request)
