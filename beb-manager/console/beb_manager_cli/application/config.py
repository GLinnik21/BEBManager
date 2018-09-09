import os


APP_DATA_DIRECTORY = os.path.join(os.environ['HOME'], '.beb-manager')
LIB_DATABASE = os.path.join(APP_DATA_DIRECTORY, 'beb-manager.db')
APP_DATABASE = os.path.join(APP_DATA_DIRECTORY, 'cli-beb-manager.db')
CONFIG_FILE = os.path.join(APP_DATA_DIRECTORY, 'config.ini')
LOG_FILE = os.path.join(APP_DATA_DIRECTORY, 'beb-manager.log')
LOG_DATEFMT = "%d/%m/%Y %H:%M:%S"
LOG_FORMAT = '%(asctime)s, %(name)s, [%(levelname)s]: %(message)s'
LOG_LEVEL = "DEBUG"
