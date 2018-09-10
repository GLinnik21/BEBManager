"""
the stupid library for task tracking

All public methods for working with task manager are located in beb_lib.model.model module.

This library works with 4 main entities: Board, List, Card, Tag. Their models are located in beb_lib.domain_entities package.

Main mediator:

    Managing all these entities is pretty simple. You should use the main Model mediator from beb_lib.model.model module and use appropriate methods to READ, WRITE or DELETE particular entity.
    You should only specify the path to a database. 
    
    >>> from beb_lib.model.model import Model
    >>> model = Model("path_to_db.db")
    
    Also, this mediator may be configured with a custom Storage Provider that conforms to IProvider abstract class from beb_lib.provider_interfaces module and IStorageProviderProtocol from beb_lib.storage.provider_interfaces module.

Creating board:

    >>> from beb_lib.model.model import Model
    >>> model = Model('mydb.db')
    >>> board = model.board_write(board_name="Hello board", request_user_id=1)

    Board comes with 3 default lists: "To Do", "In Progress" and "Done". Also, every database has its own system Archived list shared across all boards.

Getting available lists:

    >>> from beb_lib.model.model import Model
    >>> model = Model('mydb.db')
    >>> board = model.board_write(board_name="Hello board", request_user_id=1)
    >>> lists = model.list_read(board.unique_id, request_user_id=1)
    
Creating card:

    >>> from beb_lib.model.model import Model
    >>> from beb_lib.domain_entities.card import Card
    >>> model = Model('mydb.db')
    >>> board = model.board_write(board_name="Hello board", request_user_id=1)
    >>> card = Card("Hello card")
    >>> card = model.card_write(list_id=2, card_instance=card, request_user_id=1)

Creating plan for periodical card:
    
    >>> from beb_lib.model.model import Model
    >>> from beb_lib.domain_entities.card import Card
    >>> model = Model('mydb.db')
    >>> board = model.board_write(board_name="Hello board", request_user_id=1)
    >>> card = Card("Hello card")
    >>> card = model.card_write(list_id=2, card_instance=card, request_user_id=1)
    >>> model.plan_write(card_id=card.unique_id, user_id=1, interval=datetime.timedelta(days=1), last_created=datetime.datetime.now())
"""

__author__ = 'Gleb Linnik'