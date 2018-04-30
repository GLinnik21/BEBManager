import unittest
from core.entity.domain_entites import *


class TestDomainEntitiesCreation(unittest.TestCase):

    def test_unique_object_creation(self):
        name = "Name"
        uid = "ea04de40-a0ac-4c2f-9060-6b359aefb90a"

        u_object = UniqueObject(name, uid)

        self.assertIsNot(u_object, None)
        self.assertEqual(u_object.name, name)
        self.assertEqual(u_object._unique_identifier, uuid.UUID(uid))

    def test_tag_creation(self):
        tag = Tag("Yellow tag", "FF0000", unique_id="ea04de40-a0ac-4c2f-9060-6b359aefb90a")

        self.assertIsNot(tag, None)

    def test_card_creation(self):
        name = "Hello wold"
        description = "Just another hello world card"
        attachment = Card("Attachment card")
        parent_card = Card("Parent")
        first_child_card = Card("1 child")
        second_child_card = Card("2 child")
        tag = Tag("Yellow tag", "FF0000", unique_id="ea04de40-a0ac-4c2f-9060-6b359aefb90a")
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
        first_object = UniqueObject()
        second_object = UniqueObject("Hello", "ea04de40-a0ac-4c2f-9060-6b359aefb90a")

        container = UniversalContainer("Cards list", unique_id="ea04de40-a0ac-4c2f-9060-6b359aefb90a",
                                       unique_objects=[first_object, second_object])

        self.assertIsNot(container, None)
        self.assertIn(first_object, container.unique_objects)
        self.assertIn(second_object, container.unique_objects)
