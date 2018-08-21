import datetime
from peewee import (
    Proxy,
    Model,
    PrimaryKeyField,
    IntegerField,
    CharField,
    ForeignKeyField,
    DateTimeField)

from beb_lib.domain_entities import (
    Priority,
    AccessType)

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


class Board(BaseNameModel):
    pass


class CardList(BaseNameModel):
    board = ForeignKeyField(Board, backref='card_lists', null=True)


class Tag(BaseNameModel):
    user_id = IntegerField(null=True)
    color = IntegerField(null=True)


class Card(BaseNameModel):
    description = CharField(default="")
    expiration_date = DateTimeField(null=True)
    priority = IntegerField(default=Priority.MEDIUM.value)
    user_id = IntegerField(null=True)
    parent_task_id = IntegerField(null=True)
    tag = ForeignKeyField(Tag, backref='cards', null=True)
    created = DateTimeField(default=datetime.datetime.now)
    last_modified = DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        self.last_modified = datetime.datetime.now()
        return super(Card, self).save(*args, **kwargs)


class TagCard(BaseNameModel):
    """
    Made for many-to-many relation
    """
    tag = ForeignKeyField(Tag)
    card = ForeignKeyField(Card)


class CardUserAccess(BaseNameModel):
    user_id = IntegerField(null=True)
    access_type = IntegerField(default=AccessType.READ_WRITE.value)
    card = ForeignKeyField(Card)


class CardListUserAccess(BaseNameModel):
    user_id = IntegerField(null=True)
    access_type = IntegerField(default=AccessType.READ_WRITE.value)
    card_list = ForeignKeyField(CardList)


class BoardUserAccess(BaseNameModel):
    user_id = IntegerField(null=True)
    access_type = IntegerField(default=AccessType.READ_WRITE.value)
    board = ForeignKeyField(Board)


class Comment(BaseModel):
    card = ForeignKeyField(Card, backref="comments")
    comment = CharField()
