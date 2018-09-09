import random
from collections import namedtuple
from typing import List

from peewee import DoesNotExist

import beb_lib.storage.provider as provider
from beb_lib.domain_entities.tag import Tag
from beb_lib.provider_interfaces import BaseError, RequestType
from beb_lib.storage.models import TagModel, TagCard
from beb_lib.storage.provider_requests import TagDataRequest

METHOD_MAP = {
    RequestType.WRITE: lambda request: write_tag(request),
    RequestType.READ: lambda request: read_tag(request),
    RequestType.DELETE: lambda request: delete_tag(request)
}


def write_tag(request: TagDataRequest) -> (List[TagModel], BaseError):
    try:
        tag_model = None
        if request.id is not None:
            tag_model = TagModel.get(TagModel.id == request.id)
        elif request.name is not None:
            tag_model = TagModel.get(TagModel.name == request.name)

        tag_model.name = request.name
        if request.color is not None:
            tag_model.color = request.color
        tag_model.save()

        return [Tag(tag_model.name, tag_model.id, tag_model.color)], None
    except DoesNotExist:
        color = request.color if request.color is not None else random.randrange(0xFFFFFF + 1)
        tag_model = TagModel.create(name=request.name, color=color)
        return [Tag(tag_model.name, tag_model.id, tag_model.color)], None


def read_tag(request: TagDataRequest) -> (List[TagModel], BaseError):
    if request.id is None and request.name is None:
        tag_models = TagModel.select()
        return [Tag(tag_model.name, tag_model.id, tag_model.color) for tag_model in tag_models], None
    else:
        try:
            tag_model = TagModel.get((TagModel.id == request.id) | (TagModel.name == request.name))
            return [Tag(tag_model.name, tag_model.id, tag_model.color)], None
        except DoesNotExist:
            return None, BaseError(code=provider.StorageProviderErrors.TAG_DOES_NOT_EXIST,
                                   description="Tag doesn't exist")


def delete_tag(request: TagDataRequest) -> (List[TagModel], BaseError):
    try:
        tag_model = TagModel.get((TagModel.id == request.id) | (TagModel.name == request.name))
        TagCard.delete().where(TagCard.tag == tag_model).execute()
        tag_model.delete_instance()
    except DoesNotExist:
        return None, BaseError(code=provider.StorageProviderErrors.TAG_DOES_NOT_EXIST,
                               description="Tag doesn't exist")
    return None, None


def process_tag_call(request: TagDataRequest) -> (namedtuple, BaseError):
    tags, error = METHOD_MAP[request.request_type](request)
    return provider.TagDataResponse(tags=tags, request_id=request.request_id), error
