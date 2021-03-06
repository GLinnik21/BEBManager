import datetime
from collections import namedtuple

from beb_lib.domain_entities.supporting import AccessType
from beb_lib.storage.access_validator import check_access_to_card
from peewee import DoesNotExist

import beb_lib.storage.provider as provider
from beb_lib.domain_entities.plan import Plan
from beb_lib.provider_interfaces import BaseError, RequestType
from beb_lib.storage.models import CardModel, PlanModel
from beb_lib.storage.provider_requests import PlanDataRequest, PlanTriggerRequest

METHOD_MAP = {
    RequestType.WRITE: lambda request, user_id, card: write_plan(request, user_id, card),
    RequestType.READ: lambda request, user_id, card: read_plan(user_id, card),
    RequestType.DELETE: lambda request, user_id, card: delete_plan(user_id, card)
}


def create_cards_by_plans():
    for plan in PlanModel.select():
        if (plan.last_created_at + datetime.timedelta(seconds=plan.interval)) < datetime.datetime.now():
            try:
                last_created_at = plan.last_created_at
                while last_created_at + datetime.timedelta(seconds=plan.interval) < datetime.datetime.now():
                    card = plan.card
                    card.id = None
                    card.created = last_created_at
                    card.save()
                    last_created_at += datetime.timedelta(seconds=plan.interval)
                plan.last_created_at = last_created_at
                plan.save()
            except DoesNotExist:
                pass


def write_plan(request: PlanDataRequest, user_id: int, card: CardModel) -> (Plan, BaseError):
    if bool(check_access_to_card(card, user_id) & AccessType.WRITE):
        try:
            plan_model = PlanModel.get(PlanModel.card == card)
            if request.interval is not None:
                plan_model.interval = request.interval.total_seconds()
            if request.last_created is not None:
                plan_model.last_created_at = request.last_created
            plan_model.save()
        except DoesNotExist:
            plan_model = PlanModel.create(card=card, interval=request.interval.total_seconds(),
                                          last_created_at=request.last_created)
        return Plan(datetime.timedelta(seconds=plan_model.interval),
                    card.id,
                    plan_model.last_created_at,
                    plan_model.id), None
    else:
        return None, BaseError(code=provider.StorageProviderErrors.ACCESS_DENIED,
                               description="This user can't write to this card")


def read_plan(user_id: int, card: CardModel) -> (Plan, BaseError):
    if bool(check_access_to_card(card, user_id) & AccessType.READ):
        try:
            plan_model = PlanModel.get(PlanModel.card == card)
            return Plan(datetime.timedelta(seconds=plan_model.interval),
                        card.id,
                        plan_model.last_created_at, plan_model.id), None
        except DoesNotExist:
            return None, BaseError(code=provider.StorageProviderErrors.PLAN_DOES_NOT_EXIST,
                                   description="There is no plan for this task")
    else:
        return None, BaseError(code=provider.StorageProviderErrors.ACCESS_DENIED,
                               description="This user can't read this card")


def delete_plan(user_id: int, card: CardModel) -> (None, BaseError):
    if bool(check_access_to_card(card, user_id) & AccessType.WRITE):
        count = PlanModel.delete().where(PlanModel.card == card).execute()
        if count == 0:
            return None, BaseError(code=provider.StorageProviderErrors.PLAN_DOES_NOT_EXIST,
                                   description="There is no plan for this task")
    return None, None


def process_plan_call(request: PlanDataRequest) -> (namedtuple, BaseError):
    if type(request) == PlanTriggerRequest:
        return create_cards_by_plans()

    try:
        card = CardModel.get(CardModel.id == request.card_id)
        user_id = request.request_user_id
        plan_response, error = METHOD_MAP[request.request_type](request, user_id, card)

        return provider.PlanDataResponse(plan=plan_response, request_id=request.request_id), error
    except DoesNotExist:
        return None, BaseError(code=provider.StorageProviderErrors.CARD_DOES_NOT_EXIST,
                               description="Card doesn't exist")
