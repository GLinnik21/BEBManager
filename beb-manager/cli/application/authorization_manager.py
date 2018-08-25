import configparser
from typing import Optional

from storage import UserInstance

_LOGGED_USER_KEY: str = 'LoggedUser'


class AuthorizationManager:

    def __init__(self, config_file):
        self.config_file = config_file
        self.config_parser = configparser.ConfigParser()

    def login_user(self, user: UserInstance) -> None:
        self.config_parser[_LOGGED_USER_KEY] = {'unique_id': user.unique_id}
        with open(self.config_file, 'w') as configfile:
            self.config_parser.write(configfile)

    def logout_user(self) -> None:
        self.config_parser[_LOGGED_USER_KEY] = {}
        with open(self.config_file, 'w') as configfile:
            self.config_parser.write(configfile)

    def get_current_user_id(self) -> Optional[int]:
        try:
            self.config_parser.read(self.config_file)
            user_id = self.config_parser[_LOGGED_USER_KEY]['unique_id']
        except KeyError:
            return None

        return user_id
