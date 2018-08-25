import unittest
from library.domain_entities import *


class TestDomainEntitiesCreation(unittest.TestCase):

    def test_unique_object_creation(self):
        name = "Name"
        uid = "ea04de40-a0ac-4c2f-9060-6b359aefb90a"

        u_object = UniqueObject(name, uid)

        self.assertIsNot(u_object, None)
        self.assertEqual(u_object.name, name)
        self.assertEqual(u_object.unique_identifier, uuid.UUID(uid))

    def test_tag_creation(self):
        tag = Tag("Yellow tag", "ea04de40-a0ac-4c2f-9060-6b359aefb90a", "FF0000")

        self.assertIsNot(tag, None)

    def test_user_creation(self):
        user = User("Beb", unique_id="ea04de40-a0ac-4c2f-9060-6b359aefb90a", password_hash="hash")

        self.assertIsNot(user, None)

    def test_card_creation(self):
        name = "Hello wold"
        description = "Just another hello world card"
        attachment = Card("Attachment card")
        parent_card = Card("Parent")
        first_child_card = Card("1 child")
        second_child_card = Card("2 child")
        tag = Tag("Yellow tag", "ea04de40-a0ac-4c2f-9060-6b359aefb90a", "FF0000")
        priority = 100

        card = Card(name, description=description,
                    attachments=[attachment], children=[first_child_card, second_child_card],
                    parent=parent_card, tags=[tag], priority=priority)

        self.assertIsNot(card, None)
        self.assertEqual(card.name, name)
        self.assertEqual(card.description, description)
        self.assertEqual(card.priority, priority)
        self.assertIn(attachment, card.attachments)
        self.assertIn(first_child_card, card.children)
        self.assertIn(tag, card.tags)
        self.assertIs(parent_card, card.parent)

    def test_universal_container_creation(self):
        first_object = Card("Card")
        second_object = Card("Hello", "ea04de40-a0ac-4c2f-9060-6b359aefb90a")

        container = CardsList("Cards list", "ea04de40-a0ac-4c2f-9060-6b359aefb90a", [first_object, second_object])

        self.assertIsNot(container, None)
        self.assertIn(first_object, container.cards)
        self.assertIn(second_object, container.cards)
