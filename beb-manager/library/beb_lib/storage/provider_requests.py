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

TagDataRequest = namedtuple('TagDataRequest', REQUEST_BASE_FIELDS + ['id', 'name', 'color'])

PlanDataRequest = namedtuple('PlanDataRequest', REQUEST_ACCESS_FIELDS + ['interval',
                                                                         'last_created',
                                                                         'card_id'])

PlanTriggerRequest = namedtuple('PlanTriggerRequest', REQUEST_BASE_FIELDS)


class RemoveAccessRightRequest(AddAccessRightRequest):
    pass
