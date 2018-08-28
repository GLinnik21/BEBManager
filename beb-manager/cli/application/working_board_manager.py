import configparser
from typing import Optional

_WORKING_BOARD_KEY: str = 'WorkingBoard'


class WorkingBoardManager:

    def __init__(self, config_file):
        self.config_file = config_file
        self.config_parser = configparser.ConfigParser()

    def switch_to_boards(self, board_id: int) -> None:
        self.config_parser[_WORKING_BOARD_KEY] = {'unique_id': board_id}
        with open(self.config_file, 'w') as configfile:
            self.config_parser.write(configfile)

    def get_current_board_id(self) -> Optional[int]:
        try:
            self.config_parser.read(self.config_file)
            user_id = self.config_parser[_WORKING_BOARD_KEY]['unique_id']
        except KeyError:
            return None

        return user_id
