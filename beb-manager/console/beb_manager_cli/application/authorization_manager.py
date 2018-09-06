import configparser
from typing import Optional

_LOGGED_USER_SECTION: str = 'LoggedUser'


class AuthorizationManager:

    def __init__(self, config_file):
        self.config_file = config_file
        self.config_parser = configparser.ConfigParser()

    def login_user(self, user_id: int) -> None:
        self.config_parser.read(self.config_file)
        if not self.config_parser.has_section(_LOGGED_USER_SECTION):
            self.config_parser.add_section(_LOGGED_USER_SECTION)
        self.config_parser[_LOGGED_USER_SECTION]['unique_id'] = str(user_id)
        with open(self.config_file, 'w') as configfile:
            self.config_parser.write(configfile)

    def logout_user(self) -> None:
        self.config_parser.read(self.config_file)
        self.config_parser[_LOGGED_USER_SECTION] = {}
        with open(self.config_file, 'w') as configfile:
            self.config_parser.write(configfile)

    def get_current_user_id(self) -> Optional[int]:
        try:
            self.config_parser.read(self.config_file)
            user_id = int(self.config_parser[_LOGGED_USER_SECTION]['unique_id'])
        except KeyError:
            return None

        return user_id
