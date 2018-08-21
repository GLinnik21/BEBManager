from peewee import (Model,
                    PrimaryKeyField,
                    CharField,
                    Proxy)

DATABASE_PROXY = Proxy()


class UserInstance:
    """
    Class for storing user
    """

    def __init__(self, name, unique_id=None):
        self.name = name
        self.unique_id = unique_id


class User(Model):
    """
    User model
    """

    id = PrimaryKeyField(null=False)
    username = CharField()

    class Meta:
        database = DATABASE_PROXY
