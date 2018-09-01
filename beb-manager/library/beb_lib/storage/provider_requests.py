from collections import namedtuple

from beb_lib.provider_interfaces import REQUEST_ACCESS_FIELDS, REQUEST_BASE_FIELDS

BoardDataRequest = namedtuple('BoardDataRequest', REQUEST_ACCESS_FIELDS + ['id', 'name'])

ListDataRequest = namedtuple('ListDataRequest', REQUEST_ACCESS_FIELDS + ['id', 'name', 'board_id'])

CardDataRequest = namedtuple('CardDataRequest', REQUEST_ACCESS_FIELDS + ['id',
                                                                         'name',
                                                                         'description',
                                                                         'expiration_date',
                                                                         'priority',
                                                                         'assignee',
                                                                         'children',
                                                                         'tags',
                                                                         'list_id'])

GetAccessRightRequest = namedtuple('GetAccessRightRequest', REQUEST_BASE_FIELDS + ['object_type',
                                                                                   'object_id',
                                                                                   'user_id'])

AddAccessRightRequest = namedtuple('AddAccessRightRequest', REQUEST_BASE_FIELDS + ['object_type',
                                                                                   'object_id',
                                                                                   'user_id',
                                                                                   'access_type'])


class RemoveAccessRightRequest(AddAccessRightRequest):
    pass
