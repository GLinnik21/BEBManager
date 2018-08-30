from collections import namedtuple

from beb_lib import REQUEST_ACCESS_FIELDS, REQUEST_BASE_FIELDS

BoardDataRequest = namedtuple('BoardDataRequest', REQUEST_ACCESS_FIELDS + ['id', 'name'])

CardDataRequest = namedtuple('CardDataRequest', REQUEST_ACCESS_FIELDS + ['id',
                                                                         'name',
                                                                         'user',
                                                                         'description',
                                                                         'expiration_date',
                                                                         'priority',
                                                                         'parent',
                                                                         'children',
                                                                         'tags',
                                                                         'comments',
                                                                         'list'])

AddAccessRightRequest = namedtuple('AddAccessRightRequest', REQUEST_BASE_FIELDS + ['object_type',
                                                                                   'object_id',
                                                                                   'user_id',
                                                                                   'access_type'])


class ListDataRequest(BoardDataRequest):
    pass


class RemoveAccessRightRequest(AddAccessRightRequest):
    pass
