import datetime
from peewee import (
    Proxy,
    Model,
    PrimaryKeyField,
    IntegerField,
    CharField,
    ForeignKeyField,
    DateTimeField
)

from beb_lib.domain_entities.supporting import Priority, AccessType

DATABASE_PROXY = Proxy()


class BaseModel(Model):
    """
    A base model class which specifies our database.
    """
    id = PrimaryKeyField(null=False)

    class Meta:
        database = DATABASE_PROXY


class BaseNameModel(BaseModel):
    name = CharField()


class BoardModel(BaseNameModel):
    pass


class CardListModel(BaseNameModel):
    board = ForeignKeyField(BoardModel, backref='card_lists', null=True)


class TagModel(BaseNameModel):
    color = IntegerField()


class CardModel(BaseNameModel):
    description = CharField(null=True)
    expiration_date = DateTimeField(null=True)
    priority = IntegerField(default=Priority.MEDIUM.value)
    user_id = IntegerField()
    assignee_id = IntegerField(null=True)
    list = ForeignKeyField(CardListModel, backref='cards', null=True)
    created = DateTimeField(default=datetime.datetime.now)
    last_modified = DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        self.last_modified = datetime.datetime.now()
        return super(CardModel, self).save(*args, **kwargs)


class PlanModel(BaseModel):
    id = PrimaryKeyField(null=False)
    card = ForeignKeyField(CardModel, backref='plan', null=True)
    interval = IntegerField()
    last_created_at = DateTimeField()


class ParentChild(BaseModel):
    """
    Made for many-to-many relation
    """
    parent = ForeignKeyField(CardModel)
    child = ForeignKeyField(CardModel)


class TagCard(BaseModel):
    """
    Made for many-to-many relation
    """
    tag = ForeignKeyField(TagModel)
    card = ForeignKeyField(CardModel)


class CardUserAccess(BaseModel):
    user_id = IntegerField(null=True)
    access_type = IntegerField(default=AccessType.READ_WRITE.value)
    card = ForeignKeyField(CardModel)


class CardListUserAccess(BaseModel):
    user_id = IntegerField(null=True)
    access_type = IntegerField(default=AccessType.READ_WRITE.value)
    card_list = ForeignKeyField(CardListModel)


class BoardUserAccess(BaseModel):
    user_id = IntegerField(null=True)
    access_type = IntegerField(default=AccessType.READ_WRITE.value)
    board = ForeignKeyField(BoardModel)
