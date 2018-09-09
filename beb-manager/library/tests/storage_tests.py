import datetime
import random
import string
import unittest

from beb_lib.domain_entities.board import Board
from beb_lib.domain_entities.card import Card
from beb_lib.domain_entities.card_list import CardsList
from beb_lib.domain_entities.supporting import Priority, AccessType
from beb_lib.domain_entities.tag import Tag
from beb_lib.provider_interfaces import RequestType
from beb_lib.storage.provider import StorageProvider
from beb_lib.storage.provider_requests import (BoardDataRequest,
                                               ListDataRequest,
                                               CardDataRequest,
                                               TagDataRequest,
                                               PlanDataRequest, RemoveAccessRightRequest,
                                               GetAccessRightRequest
                                               )


class StorageTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.data_base = ':memory:'
        cls.storage_provider = StorageProvider(cls.data_base)

    @classmethod
    def tearDownClass(cls):
        cls.storage_provider.close()

    def setUp(self):
        self.storage_provider.open()

    def tearDown(self):
        self.storage_provider._drop_tables()

    def create_test_board(self, user_id=random.randrange(1000)) -> Board:
        request = BoardDataRequest(request_id=random.randrange(1000000),
                                   request_user_id=user_id,
                                   id=None,
                                   name="Some name",
                                   request_type=RequestType.WRITE)
        result, error = self.storage_provider.execute(request)

        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.boards)
        self.assertNotEqual(len(result.boards), 0)

        board = result.boards[0]

        self.assertIsNotNone(board.unique_id)
        self.assertEqual(board.name, request.name)

        return board

    def create_test_list(self, user_id: int = random.randrange(1000), board_id: int = None) -> CardsList:
        if board_id is None:
            board_id = self.create_test_board().unique_id

        request = ListDataRequest(request_id=random.randrange(1000000),
                                  board_id=board_id,
                                  request_user_id=user_id,
                                  id=None,
                                  name="Some name",
                                  request_type=RequestType.WRITE)
        result, error = self.storage_provider.execute(request)

        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.lists)
        self.assertNotEqual(len(result.lists), 0)

        card_list = result.lists[0]

        self.assertIsNotNone(card_list.unique_id)
        self.assertEqual(card_list.name, request.name)

        return card_list

    def create_test_tag(self) -> Tag:
        request = TagDataRequest(request_id=random.randrange(1000000),
                                 id=None,
                                 name=''.join(random.choices(string.ascii_letters + string.digits, k=6)),
                                 color=random.randrange(0xFFFFFF + 1),
                                 request_type=RequestType.WRITE)

        result, error = self.storage_provider.execute(request)

        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.tags)
        self.assertNotEqual(len(result.tags), 0)

        tag = result.tags[0]

        self.assertIsNotNone(tag.unique_id)
        self.assertEqual(tag.name, request.name)
        self.assertEqual(tag.color, request.color)

        return tag

    def create_test_card(self, list_id: int = None, user_id: int = random.randrange(1000)) -> Card:
        if list_id is None:
            list_id = self.create_test_list(user_id).unique_id

        tags = [self.create_test_tag().unique_id, self.create_test_tag().unique_id, self.create_test_tag().unique_id]

        request = CardDataRequest(request_id=random.randrange(1000000),
                                  id=None,
                                  request_user_id=user_id,
                                  name="Some name",
                                  description="Some description",
                                  expiration_date=datetime.datetime.now() + datetime.timedelta(days=2),
                                  priority=Priority.HIGH,
                                  assignee=random.randrange(11),
                                  children=None,
                                  tags=tags,
                                  list_id=list_id,
                                  request_type=RequestType.WRITE)

        result, error = self.storage_provider.execute(request)

        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.cards)
        self.assertNotEqual(len(result.cards), 0)

        card = result.cards[0]

        self.assertEqual(card.name, request.name)
        self.assertEqual(card.description, request.description)
        self.assertEqual(card.expiration_date, request.expiration_date)
        self.assertEqual(card.priority, request.priority)
        self.assertEqual(card.assignee_id, request.assignee)
        self.assertEqual(card.user_id, user_id)

        for tag in tags:
            self.assertIn(tag, card.tags)

        return card

    def test_board_write(self):
        self.create_test_board()

    def test_board_rewrite(self):
        user_id = random.randrange(1000)

        board = self.create_test_board(user_id)

        request = BoardDataRequest(request_id=random.randrange(1000000),
                                   request_user_id=user_id,
                                   id=board.unique_id,
                                   name="Another name",
                                   request_type=RequestType.WRITE)

        result, error = self.storage_provider.execute(request)

        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.boards)
        self.assertNotEqual(len(result.boards), 0)
        board = result.boards[0]

        self.assertEqual(board.name, request.name)
        self.assertEqual(board.unique_id, request.id)

    def test_board_read(self):
        user_id = random.randrange(1000)

        first_board = self.create_test_board(user_id)

        request = BoardDataRequest(request_id=random.randrange(1000000),
                                   request_user_id=user_id,
                                   id=first_board.unique_id,
                                   name=None,
                                   request_type=RequestType.READ)

        result, error = self.storage_provider.execute(request)

        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.boards)
        self.assertNotEqual(len(result.boards), 0)

        second_board = result.boards[0]

        self.assertEqual(first_board.unique_id, second_board.unique_id)
        self.assertEqual(first_board.name, second_board.name)

    def test_board_read_many(self):
        user_id = random.randrange(1000)

        boards = [self.create_test_board(user_id), self.create_test_board(user_id), self.create_test_board(user_id)]

        request = BoardDataRequest(request_id=random.randrange(1000000),
                                   request_user_id=user_id,
                                   id=None,
                                   name=None,
                                   request_type=RequestType.READ)

        result, error = self.storage_provider.execute(request)

        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.boards)
        self.assertEqual(len(result.boards), len(boards))

        ids = [b.unique_id for b in result.boards]

        for board in boards:
            self.assertIn(board.unique_id, ids)

    def test_board_delete(self):
        user_id = random.randrange(1000)

        board = self.create_test_board(user_id)

        request = BoardDataRequest(request_id=random.randrange(1000000),
                                   request_user_id=user_id,
                                   id=board.unique_id,
                                   name=None,
                                   request_type=RequestType.DELETE)

        result, error = self.storage_provider.execute(request)

        self.assertIsNone(error)

    def test_list_write(self):
        self.create_test_list()

    def test_list_rewrite(self):
        user_id = random.randrange(1000)

        first_board = self.create_test_board(user_id)
        second_board = self.create_test_board(user_id)

        card_list = self.create_test_list(user_id, first_board.unique_id)

        request = ListDataRequest(request_id=random.randrange(1000000),
                                  board_id=second_board.unique_id,
                                  request_user_id=user_id,
                                  id=card_list.unique_id,
                                  name="Another name",
                                  request_type=RequestType.WRITE)

        result, error = self.storage_provider.execute(request)

        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.lists)
        self.assertNotEqual(len(result.lists), 0)

        card_list = result.lists[0]

        self.assertEqual(card_list.name, request.name)
        self.assertEqual(card_list.unique_id, request.id)

    def test_list_read(self):
        user_id = random.randrange(1000)

        card_list = self.create_test_list(user_id)

        request = ListDataRequest(request_id=random.randrange(1000000),
                                  board_id=None,
                                  request_user_id=user_id,
                                  id=card_list.unique_id,
                                  name=None,
                                  request_type=RequestType.READ)

        result, error = self.storage_provider.execute(request)

        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.lists)
        self.assertNotEqual(len(result.lists), 0)

        read_card_list = result.lists[0]

        self.assertEqual(read_card_list.name, card_list.name)
        self.assertEqual(read_card_list.unique_id, card_list.unique_id)

    def test_lists_read_many(self):
        user_id = random.randrange(1000)

        lists = [self.create_test_list(user_id), self.create_test_list(user_id), self.create_test_list(user_id)]

        request = ListDataRequest(request_id=random.randrange(1000000),
                                  board_id=None,
                                  request_user_id=user_id,
                                  id=None,
                                  name=None,
                                  request_type=RequestType.READ)

        result, error = self.storage_provider.execute(request)

        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.lists)

        ids = [l.unique_id for l in result.lists]

        self.assertIn(lists[0].unique_id, ids)
        self.assertIn(lists[1].unique_id, ids)
        self.assertIn(lists[2].unique_id, ids)

    def test_list_delete(self):
        user_id = random.randrange(1000)

        card_list = self.create_test_list(user_id=user_id, board_id=None)

        request = ListDataRequest(request_id=random.randrange(1000000),
                                  board_id=None,
                                  request_user_id=user_id,
                                  id=card_list.unique_id,
                                  name=None,
                                  request_type=RequestType.DELETE)

        result, error = self.storage_provider.execute(request)

        self.assertIsNone(error)

    def test_card_write(self):
        self.create_test_card()

    def test_card_rewrite(self):
        user_id = random.randrange(1000)

        card = self.create_test_card()
        card_list = self.create_test_list(user_id)

        tags = card.tags
        tags.remove(random.choice(tags))

        request = CardDataRequest(request_id=random.randrange(1000000),
                                  id=None,
                                  request_user_id=user_id,
                                  name="Another name",
                                  description="Another description",
                                  expiration_date=datetime.datetime.now() + datetime.timedelta(days=3),
                                  priority=Priority.MEDIUM,
                                  assignee=random.randrange(11),
                                  children=None,
                                  tags=tags,
                                  list_id=card_list.unique_id,
                                  request_type=RequestType.WRITE)

        result, error = self.storage_provider.execute(request)

        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.cards)
        self.assertNotEqual(len(result.cards), 0)

        new_card = result.cards[0]

        self.assertEqual(new_card.name, request.name)
        self.assertEqual(new_card.description, request.description)
        self.assertEqual(new_card.expiration_date, request.expiration_date)
        self.assertEqual(new_card.priority, request.priority)
        self.assertEqual(new_card.assignee_id, request.assignee)
        self.assertEqual(new_card.user_id, user_id)

        for tag in tags:
            self.assertIn(tag, card.tags)

    def test_card_read(self):
        card = self.create_test_card()

        request = CardDataRequest(request_id=random.randrange(1000000),
                                  id=card.unique_id,
                                  request_user_id=card.user_id,
                                  name=None,
                                  description=None,
                                  expiration_date=None,
                                  priority=None,
                                  assignee=None,
                                  children=None,
                                  tags=[],
                                  list_id=None,
                                  request_type=RequestType.READ)

        result, error = self.storage_provider.execute(request)

        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.cards)
        self.assertNotEqual(len(result.cards), 0)

        read_card = result.cards[0]

        self.assertEqual(card.name, read_card.name)
        self.assertEqual(card.description, read_card.description)
        self.assertEqual(card.expiration_date, read_card.expiration_date)
        self.assertEqual(card.priority, read_card.priority)
        self.assertEqual(card.assignee_id, read_card.assignee_id)
        self.assertEqual(card.user_id, read_card.user_id)

        for tag in read_card.tags:
            self.assertIn(tag, card.tags)

    def test_card_read_many(self):
        user_id = random.randrange(1000)
        cards = [self.create_test_card(user_id=user_id),
                 self.create_test_card(user_id=user_id),
                 self.create_test_card(user_id=user_id)]

        request = CardDataRequest(request_id=random.randrange(1000000),
                                  id=None,
                                  request_user_id=user_id,
                                  name=None,
                                  description=None,
                                  expiration_date=None,
                                  priority=None,
                                  assignee=None,
                                  children=None,
                                  tags=None,
                                  list_id=None,
                                  request_type=RequestType.READ)

        result, error = self.storage_provider.execute(request)

        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.cards)
        self.assertEqual(len(result.cards), len(cards))

    def test_card_delete(self):
        card = self.create_test_card()

        request = CardDataRequest(request_id=random.randrange(1000000),
                                  id=card.unique_id,
                                  request_user_id=card.user_id,
                                  name=None,
                                  description=None,
                                  expiration_date=None,
                                  priority=None,
                                  assignee=None,
                                  children=None,
                                  tags=None,
                                  list_id=None,
                                  request_type=RequestType.DELETE)

        result, error = self.storage_provider.execute(request)

        self.assertIsNone(error)

    def test_tag_write(self):
        self.create_test_tag()

    def test_tag_rewrite(self):
        tag = self.create_test_tag()

        request = TagDataRequest(request_id=random.randrange(1000000),
                                 id=tag.unique_id,
                                 name="New name",
                                 color=0xFFFFFF,
                                 request_type=RequestType.WRITE)

        result, error = self.storage_provider.execute(request)

        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.tags)
        self.assertNotEqual(len(result.tags), 0)

        tag = result.tags[0]

        self.assertIsNotNone(tag.unique_id)
        self.assertEqual(tag.name, request.name)
        self.assertEqual(tag.color, request.color)

    def test_tag_read_id(self):
        tag = self.create_test_tag()

        request = TagDataRequest(request_id=random.randrange(1000000),
                                 id=tag.unique_id,
                                 name=None,
                                 color=None,
                                 request_type=RequestType.READ)

        result, error = self.storage_provider.execute(request)

        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.tags)
        self.assertNotEqual(len(result.tags), 0)

        read_tag = result.tags[0]

        self.assertEqual(tag.unique_id, read_tag.unique_id)
        self.assertEqual(tag.name, read_tag.name)
        self.assertEqual(tag.color, read_tag.color)

    def test_tag_read_name(self):
        tag = self.create_test_tag()

        request = TagDataRequest(request_id=random.randrange(1000000),
                                 id=None,
                                 name=tag.name,
                                 color=None,
                                 request_type=RequestType.READ)

        result, error = self.storage_provider.execute(request)

        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.tags)
        self.assertNotEqual(len(result.tags), 0)

        read_tag = result.tags[0]

        self.assertEqual(tag.unique_id, read_tag.unique_id)
        self.assertEqual(tag.name, read_tag.name)
        self.assertEqual(tag.color, read_tag.color)

    def test_tag_read_many(self):
        tags = [self.create_test_tag(), self.create_test_tag(), self.create_test_tag()]

        request = TagDataRequest(request_id=random.randrange(1000000),
                                 id=None,
                                 name=None,
                                 color=None,
                                 request_type=RequestType.READ)

        result, error = self.storage_provider.execute(request)

        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.tags)
        self.assertEqual(len(result.tags), len(tags))

    def test_tag_delete_id(self):
        tag = self.create_test_tag()

        request = TagDataRequest(request_id=random.randrange(1000000),
                                 id=tag.unique_id,
                                 name=None,
                                 color=None,
                                 request_type=RequestType.DELETE)

        result, error = self.storage_provider.execute(request)

        self.assertIsNone(error)

    def test_card_read_tag(self):
        user_id = random.randrange(100)
        card_list = self.create_test_list()
        tags = []
        times = 10

        for i in range(times):
            tags.append(self.create_test_tag().unique_id)

        for i in range(times):
            request = CardDataRequest(request_id=random.randrange(1000000),
                                      id=None,
                                      request_user_id=user_id,
                                      name="Some name",
                                      description="Some description",
                                      expiration_date=datetime.datetime.now() + datetime.timedelta(days=2),
                                      priority=Priority.HIGH,
                                      assignee=random.randrange(11),
                                      children=None,
                                      tags=tags[:len(tags) - i],
                                      list_id=card_list.unique_id,
                                      request_type=RequestType.WRITE)

            self.storage_provider.execute(request)

        for i in range(times):
            request = CardDataRequest(request_id=random.randrange(1000000),
                                      id=None,
                                      request_user_id=user_id,
                                      name=None,
                                      description=None,
                                      expiration_date=None,
                                      priority=None,
                                      assignee=None,
                                      children=None,
                                      tags=[tags[i]],
                                      list_id=None,
                                      request_type=RequestType.READ)
            result, error = self.storage_provider.execute(request)

            self.assertIsNone(error)
            self.assertIsNotNone(result)
            self.assertIsNotNone(result.cards)
            self.assertEqual(len(result.cards), times - i)

    def test_plan_write(self):
        user_id = random.randrange(100)
        card = self.create_test_card(user_id=user_id)

        request = PlanDataRequest(request_id=random.randrange(1000000),
                                  request_user_id=user_id,
                                  interval=datetime.timedelta(seconds=300),
                                  last_created=datetime.datetime.now(),
                                  card_id=card.unique_id,
                                  request_type=RequestType.WRITE)

        result, error = self.storage_provider.execute(request)

        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.plan)

        plan = result.plan

        self.assertEqual(plan.interval, request.interval)
        self.assertEqual(plan.last_created_at, request.last_created)
        self.assertEqual(plan.card_id, request.card_id)

        request = CardDataRequest(request_id=random.randrange(1000000),
                                  id=None,
                                  request_user_id=user_id,
                                  name=None,
                                  description=None,
                                  expiration_date=None,
                                  priority=None,
                                  assignee=None,
                                  children=None,
                                  tags=[],
                                  list_id=None,
                                  request_type=RequestType.READ)
        result, error = self.storage_provider.execute(request)

        self.assertEqual(result.cards[0].plan, plan.unique_id)

    def test_access(self):
        user_id = random.randrange(100)

        board = self.create_test_board(user_id)
        card_list = self.create_test_list(user_id, board.unique_id)
        card = self.create_test_card(card_list.unique_id, user_id)

        request = GetAccessRightRequest(request_id=random.randrange(1000000),
                                        request_type=RequestType.READ,
                                        object_type=Card,
                                        object_id=card.unique_id,
                                        user_id=user_id)

        result = self.storage_provider.execute(request)

        self.assertEqual(result, AccessType.READ_WRITE)

        request = RemoveAccessRightRequest(request_id=random.randrange(1000000),
                                           request_type=RequestType.WRITE,
                                           object_type=Board,
                                           object_id=card.unique_id,
                                           user_id=user_id,
                                           access_type=AccessType.READ_WRITE)

        self.storage_provider.execute(request)

        request = GetAccessRightRequest(request_id=random.randrange(1000000),
                                        request_type=RequestType.READ,
                                        object_type=Card,
                                        object_id=card.unique_id,
                                        user_id=user_id)

        result = self.storage_provider.execute(request)

        self.assertEqual(result, AccessType.NONE)
