from collections import namedtuple
from core.entity.domain_entites import Card
from core.usecase.interfaces import IInputBoundary

CardCreationRequest = namedtuple('CardCreationRequest',
                                 ['name', 'uuid', 'description',
                                  'expiration_date', 'priority', 'attachments',
                                  'parent', 'children', 'tags',
                                  'comments', 'list_uuid'])


class CreateCardUseCase(IInputBoundary):

    def __init__(self, cards_repo=None):
        self.cards_data_repo = cards_repo

    def execute(self, request_model, output_port):
        if self.cards_data_repo is not None:
            card = Card(name=request_model.name, unique_id=request_model.uuid,
                        description=request_model.description, expiration_date=request_model.expiration_date,
                        priority=request_model.priority, comments=request_model.comments)

            parent = Card(unique_id=request_model.parent.uuid)
            children = []

            for child in request_model.children:
                children.append(Card(unique_id=child.uuid))

            card._children = children
            card.parent = parent

            self.cards_data_repo.add_card(card, request_model.list_uuid)
