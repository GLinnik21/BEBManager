import random
from typing import List, Optional

from application import config, AuthorizationManager
from beb_lib import (StorageProvider,
                     RequestType,
                     Model, BaseError)
from storage import (UserProvider,
                     UserDataRequest,
                     UserInstance)


class App:

    def __init__(self):
        self.lib_model = Model(StorageProvider(config.LIB_DATABASE))
        self.user_provider = UserProvider(config.APP_DATABASE)
        self.user_provider.open()
        self.authorization_manager = AuthorizationManager(config.CONFIG_FILE)

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

        user = self.get_user_by_id(user_id)

        if user is not None:
            self.authorization_manager.logout_user()
            print("Successfully logged out from {}".format(user.name))
        else:
            print("You were not logged in")

    def login_user(self, name: str, user_id: int) -> None:
        user = None

        if name is not None:
            user = self.get_user_by_name(name)
        elif user_id is not None:
            user = self.get_user_by_id(user_id)

        if user is None:
            print("User with provided credentials was not found")
            quit(1)

        self.authorization_manager.login_user(user)
        print("Successfully logged in as {}".format(user.name))

    def get_user_by_id(self, user_id: int) -> Optional[UserInstance]:
        request = UserDataRequest(request_id=random.randrange(1000000),
                                  id=user_id,
                                  name=None,
                                  request_type=RequestType.READ)
        result = self.user_provider.sync_execute(request)

        error: Optional[BaseError] = result[1]

        if error is not None:
            print("Database error: {}".format(result[1].description))
            quit(error.code)

        users: Optional[List[UserInstance]] = result[0].users
        if not users:
            return None
        else:
            return users[0]

    def get_user_by_name(self, name: str) -> Optional[UserInstance]:
        request = UserDataRequest(request_id=random.randrange(1000000),
                                  id=None,
                                  name=name,
                                  request_type=RequestType.READ)
        result = self.user_provider.sync_execute(request)

        error: Optional[BaseError] = result[1]

        if error is not None:
            print("Database error: {}".format(result[1].description))
            quit(error.code)

        users: Optional[List[UserInstance]] = result[0].users
        if not users:
            return None
        else:
            return users[0]

    def get_all_users(self) -> List[UserInstance]:
        request = UserDataRequest(request_id=random.randrange(1000000),
                                  id=None,
                                  name=None,
                                  request_type=RequestType.READ)
        result = self.user_provider.sync_execute(request)[0]
        users = sorted(result.users, key=lambda user: user.unique_id)
        return users

    def print_all_users(self) -> None:
        users = self.get_all_users()
        self._print_users(users)

    def print_current_user(self) -> None:
        user_id = self.authorization_manager.get_current_user_id()

        user = self.get_user_by_id(user_id)

        if user is not None:
            self._print_users([user])
        else:
            print("You were not logged in")

    @staticmethod
    def _print_users(users: List[UserInstance]) -> None:
        for user in users:
            print("UserID: {}   Name: {}".format(user.unique_id, user.name))
