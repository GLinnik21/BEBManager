import datetime
import unittest
import random

from beb_lib.domain_entities.board import Board
from beb_lib.domain_entities.card_list import CardsList
from beb_lib.domain_entities.card import Card
from beb_lib.domain_entities.plan import Plan
from beb_lib.domain_entities.supporting import Priority
from beb_lib.domain_entities.tag import Tag
from beb_lib.domain_entities.unique_object import UniqueObject


class TestDomainEntitiesCreation(unittest.TestCase):

    def test_unique_object_creation(self):
        name = "Name"
        uid = random.randrange(100)

        u_object = UniqueObject(name, uid)

        self.assertIsNot(u_object, None)
        self.assertIsInstance(u_object, UniqueObject)
        self.assertEqual(u_object.name, name)
        self.assertEqual(u_object.unique_id, uid)

    def test_tag_creation(self):
        name = "Red tag"
        uid = random.randrange(100)
        color = 0xFF0000

        tag = Tag(name, uid, color)

        self.assertIsNot(tag, None)
        self.assertIsInstance(tag, Tag)
        self.assertEqual(tag.name, name)
        self.assertEqual(tag.unique_id, uid)
        self.assertEqual(tag.color, color)

    def test_card_creation(self):
        name = "Hello wold"
        uid = random.randrange(100)
        owner = random.randrange(100)
        assignee = random.randrange(100)
        description = "Just another hello world card"
        expiration_date = datetime.datetime.now()
        priority = Priority.MEDIUM
        first_child_card = Card("1 child")
        second_child_card = Card("2 child")
        tag = Tag("Red tag", random.randrange(100), 0xFF0000)
        created = datetime.datetime.now()
        last_modified = datetime.datetime.now()

        card = Card(name, uid, owner, assignee, description, expiration_date, priority,
                    [first_child_card.unique_id, second_child_card.unique_id], [tag.unique_id], created, last_modified)

        self.assertIsNot(card, None)
        self.assertIsInstance(card, Card)
        self.assertEqual(card.name, name)
        self.assertEqual(card.description, description)
        self.assertEqual(owner, card.user_id)
        self.assertEqual(assignee, card.assignee_id)
        self.assertEqual(card.priority, priority)
        self.assertEqual(expiration_date, card.expiration_date)
        self.assertEqual(created, card.created)
        self.assertEqual(last_modified, card.last_modified)
        self.assertIn(first_child_card.unique_id, card.children)
        self.assertIn(second_child_card.unique_id, card.children)
        self.assertIn(tag.unique_id, card.tags)

    def test_board_creation(self):
        name = "Board"
        uid = random.randrange(100)
        lists = random.sample(range(1, 100), 10)

        board = Board(name, uid, lists)

        self.assertEqual(name, board.name)
        self.assertEqual(uid, board.unique_id)
        self.assertIn(random.choice(lists), board.lists)

    def test_list_creation(self):
        name = "List"
        uid = random.randrange(100)
        cards = random.sample(range(1, 100), 10)

        card_list = CardsList(name, uid, cards)

        self.assertEqual(name, card_list.name)
        self.assertEqual(uid, card_list.unique_id)
        self.assertIn(random.choice(cards), card_list.cards)

    def test_plan_creation(self):
        interval = datetime.timedelta(seconds=random.randrange(1000))
        last_created_at = datetime.datetime.now()
        uid = random.randrange(100)
        card = random.randrange(100)

        plan = Plan(interval, card, last_created_at, uid)

        self.assertEqual(interval, plan.interval)
        self.assertEqual(last_created_at, plan.last_created_at)
        self.assertEqual(uid, plan.unique_id)
        self.assertEqual(card, plan.card_id)
