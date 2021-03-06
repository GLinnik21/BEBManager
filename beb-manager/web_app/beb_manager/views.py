import datetime

import beb_lib.model.exceptions as beb_exceptions
import dateparser
import pytimeparse
from beb_lib.domain_entities.board import Board
from beb_lib.domain_entities.card import Card
from beb_lib.domain_entities.card_list import CardsList
from beb_lib.domain_entities.supporting import Priority, AccessType
from beb_lib.model.model import Model
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect

from beb_manager.forms import SingleInputForm, CardFormWithoutLists, CardForm, TagForm

MODEL = Model(settings.BEB_LIB_DATABASE_PATH)


def process_plans(func):
    def wrap(request, *args, **kwargs):
        MODEL.trigger_card_plan_creation()
        return func(request, *args, **kwargs)

    return wrap


@process_plans
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('beb_manager:boards')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@process_plans
@login_required
def boards(request):
    try:
        beb_boards = MODEL.board_read(request_user_id=request.user.id)
        Board.editable = True
        for board in beb_boards:
            board. editable = bool(MODEL.get_right(board.unique_id, Board, request.user.id) & AccessType.WRITE)
    except beb_exceptions.Error:
        beb_boards = []

    return render(request, 'beb_manager/boards/boards.html', {'user_boards': beb_boards, 'container_editable': True})


@process_plans
@login_required
def add_board(request):
    try:
        if request.method == 'POST':
            form = SingleInputForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data['name']
                try:
                    MODEL.board_write(board_name=name,
                                      request_user_id=request.user.id)
                except beb_exceptions.Error:
                    pass
                return redirect('beb_manager:boards')
        else:
            form = SingleInputForm()
        return render(request, 'beb_manager/boards/add.html', {'form': form, 'container_editable': True})
    except beb_exceptions.AccessDeniedError:
        return HttpResponse('<h1>Access Denied</h1>')
    except beb_exceptions.Error:
        return redirect('beb_manager:boards')


@process_plans
@login_required
def edit_board(request, board_id):
    try:
        board = MODEL.board_read(board_id, request_user_id=request.user.id)[0]

        if request.method == 'POST':
            form = SingleInputForm(request.POST)
            if form.is_valid():
                if 'save' in request.POST:
                    new_name = form.cleaned_data['name']

                    can_read = form.cleaned_data['can_read']
                    can_write = form.cleaned_data['can_write']

                    MODEL.board_write(board.unique_id, new_name, request_user_id=request.user.id)

                    if can_read:
                        for user in can_read:
                            MODEL.add_right(board_id, Board, user.id, AccessType.READ)
                    if can_write:
                        for user in can_write:
                            MODEL.add_right(board_id, Board, user.id, AccessType.WRITE)

                    for user in User.objects.all():
                        if user not in can_read and can_read:
                            MODEL.remove_right(board_id, Board, user.id, AccessType.READ)
                        if user not in can_write and can_write:
                            MODEL.remove_right(board_id, Board, user.id, AccessType.WRITE)
                elif 'delete' in request.POST:
                    MODEL.board_delete(board_id, request_user_id=request.user.id)
                return redirect('beb_manager:boards')
        else:
            can_write = []
            can_read = []

            for user in User.objects.all():
                if bool(MODEL.get_right(board_id, Board, user.id) & AccessType.READ):
                    can_read.append(user)
                if bool(MODEL.get_right(board_id, Board, user.id) & AccessType.WRITE):
                    can_write.append(user)

            form = SingleInputForm(initial={'name': board.name, 'can_read': can_read, 'can_write': can_write})
        editable = bool(MODEL.get_right(board_id, Board, request.user.id) & AccessType.WRITE)
        return render(request, 'beb_manager/boards/edit.html', {'form': form, 'container_editable': editable})
    except beb_exceptions.AccessDeniedError:
        return HttpResponse('<h1>Access Denied</h1>')
    except beb_exceptions.Error:
        return redirect('beb_manager:boards')


@process_plans
@login_required
def delete_board(request, board_id):
    try:
        if request.method == 'POST':
            MODEL.board_delete(board_id, request_user_id=request.user.id)
        return redirect('beb_manager:boards')
    except beb_exceptions.AccessDeniedError:
        return HttpResponse('<h1>Access Denied</h1>')


@process_plans
@login_required
def lists(request, board_id):
    try:
        tags = MODEL.tag_read()
        for i in range(len(tags)):
            tags[i].color = '#{0:06X}'.format(tags[i].color)
    except beb_exceptions.TagDoesNotExistError:
        tags = []
    editable = bool(MODEL.get_right(board_id, Board, request.user.id) & AccessType.WRITE)
    try:
        today = datetime.datetime.today()
        lists_models = MODEL.list_read(board_id, request_user_id=request.user.id)
        beb_lists = []
        Card.editable = True
        CardsList.editable = True

        for card_list in lists_models:
            card_list.editable = bool(MODEL.get_right(card_list.unique_id, CardsList, request.user.id)
                                      & AccessType.WRITE)
            try:
                cards = MODEL.card_read(card_list.unique_id, request_user_id=request.user.id)
                for card in cards:
                    card.editable = bool(MODEL.get_right(card.unique_id, Card, request.user.id) & AccessType.WRITE)
                    for i in range(len(card.tags)):
                        card.tags[i] = MODEL.tag_read(tag_id=card.tags[i])[0]
                        card.tags[i].color = '#{0:06X}'.format(card.tags[i].color)
            except beb_exceptions.CardDoesNotExistError:
                cards = []

            card_list._cards = cards
            beb_lists.append(card_list)

        return render(request, 'beb_manager/lists/lists.html',
                      {'beb_lists': beb_lists, 'board_id': board_id, 'tags': tags,
                       'today': today, 'container_editable': editable})

    except beb_exceptions.ListDoesNotExistError:
        return render(request, 'beb_manager/lists/lists.html',
                      {'beb_lists': [], 'board_id': board_id, 'tags': tags,
                       'today': today, 'container_editable': editable})
    except beb_exceptions.AccessDeniedError:
        return HttpResponse('<h1>Access Denied</h1>')
    except beb_exceptions.Error:
        return redirect('beb_manager:boards')


@process_plans
@login_required
def add_list(request, board_id):
    try:
        if request.method == 'POST':
            form = SingleInputForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data['name']
                MODEL.list_write(board_id, list_name=name,
                                 request_user_id=request.user.id)
        else:
            form = SingleInputForm()

        editable = bool(MODEL.get_right(board_id, Board, request.user.id) & AccessType.WRITE)
        return render(request, 'beb_manager/lists/add.html', {'form': form, 'container_editable': editable})
    except beb_exceptions.AccessDeniedError:
        return HttpResponse('<h1>Access Denied</h1>')


@process_plans
@login_required
def delete_list(request, board_id, list_id):
    if request.method == 'POST':
        MODEL.list_delete(list_id, request_user_id=request.user.id)
    return redirect('beb_manager:lists', board_id)


@process_plans
@login_required
def edit_list(request, board_id, list_id):
    try:
        card_list = MODEL.list_read(None, list_id, request_user_id=request.user.id)[0]

        if request.method == 'POST':
            form = SingleInputForm(request.POST)
            if form.is_valid():
                if 'save' in request.POST:
                    new_name = form.cleaned_data['name']

                    can_read = form.cleaned_data['can_read']
                    can_write = form.cleaned_data['can_write']
                    MODEL.list_write(board_id, list_id, new_name, request.user.id)

                    if can_read:
                        for user in can_read:
                            MODEL.add_right(list_id, CardsList, user.id, AccessType.READ)
                    if can_write:
                        for user in can_write:
                            MODEL.add_right(list_id, CardsList, user.id, AccessType.WRITE)

                    for user in User.objects.all():
                        if user not in can_read and can_read:
                            MODEL.remove_right(list_id, CardsList, user.id, AccessType.READ)
                        if user not in can_write and can_write:
                            MODEL.remove_right(list_id, CardsList, user.id, AccessType.WRITE)
                elif 'delete' in request.POST:
                    MODEL.list_delete(list_id, request_user_id=request.user.id)
                return redirect('beb_manager:lists', board_id)
        else:

            can_write = []
            can_read = []

            for user in User.objects.all():
                if bool(MODEL.get_right(list_id, CardsList, user.id) & AccessType.READ):
                    can_read.append(user)
                if bool(MODEL.get_right(list_id, CardsList, user.id) & AccessType.WRITE):
                    can_write.append(user)

            form = SingleInputForm(initial={'name': card_list.name, 'can_read': can_read, 'can_write': can_write})
        editable = bool(MODEL.get_right(board_id, Board, request.user.id) & AccessType.WRITE)
        return render(request, 'beb_manager/lists/edit.html', {'form': form, 'container_editable': editable})

    except beb_exceptions.AccessDeniedError:
        return HttpResponse('<h1>Access Denied</h1>')


@process_plans
@login_required
def show_card(request, board_id, card_id):
    try:
        card = MODEL.card_read(None, card_id, request_user_id=request.user.id)[0]
        card_list = MODEL.get_list_of_card(card.unique_id, request.user.id)
        Card.editable = True
        card.editable = bool(MODEL.get_right(card.unique_id, Card, request.user.id) & AccessType.WRITE)

        if card.plan is not None:
            plan = MODEL.plan_read(card.unique_id, request.user.id)
        else:
            plan = None

        card.priority = Priority(card.priority).name

        for i in range(len(card.tags)):
            card.tags[i] = MODEL.tag_read(tag_id=card.tags[i])[0]
            card.tags[i].color = '#{0:06X}'.format(card.tags[i].color)

        if card.children is not None and card.children:
            for i in range(len(card.children)):
                try:
                    child = MODEL.card_read(None, card.children[i], request_user_id=request.user.id)[0]
                    card.children[i] = child
                except beb_exceptions.Error:
                    pass

        card.assignee_id = User.objects.get(pk=card.assignee_id) if card.assignee_id is not None else None
        card.user_id = User.objects.get(pk=card.user_id)

        editable = bool(MODEL.get_right(board_id, Board, request.user.id) & AccessType.WRITE)
        return render(request, 'beb_manager/cards/show.html', {'card': card,
                                                               'card_list': card_list,
                                                               'board_id': board_id,
                                                               'plan': plan,
                                                               'container_editable': editable})
    except beb_exceptions.AccessDeniedError:
        return HttpResponse('<h1>Access Denied</h1>')
    except beb_exceptions.Error:
        return redirect('beb_manager:lists', board_id)


@process_plans
@login_required
def add_card(request, board_id, list_id):
    try:
        if request.method == 'POST':
            form = CardFormWithoutLists(request.user.id, board_id, request.POST)
            name = form.data['name']
            if name is None or name == '' or name.isspace():
                form.add_error('name', "Name should not be empty")

            interval = form.data['interval']
            if interval == '' or interval.isspace():
                interval = None

            if interval is not None:
                interval = pytimeparse.parse(interval)
                if interval is None:
                    form.add_error('interval', "Interval is incorrect")
                if interval < 300:  # 5 minutes
                    form.add_error('interval', "Interval should be more than 5 minutes")

            if form.is_valid():
                name = form.cleaned_data['name']
                description = form.cleaned_data['description']
                tags = []
                for tag in form.cleaned_data['tags']:
                    try:
                        tags.append(int(tag))
                    except ValueError:
                        pass
                children_cards = []
                for card in form.cleaned_data['children_cards']:
                    try:
                        children_cards.append(int(card))
                    except ValueError:
                        pass
                exp_date = form.cleaned_data['expiration_date']
                priority = form.cleaned_data['priority']
                assignee_user = form.cleaned_data['assignee']
                assignee = assignee_user.id if assignee_user is not None else None

                can_read = form.cleaned_data['can_read']
                can_write = form.cleaned_data['can_write']

                new_card = Card(name=name,
                                description=description,
                                assignee_id=assignee,
                                expiration_date=exp_date,
                                priority=priority,
                                tags=tags,
                                children=children_cards)
                new_card = MODEL.card_write(list_id, new_card, request.user.id)

                if can_read:
                    for user in can_read:
                        MODEL.add_right(new_card.unique_id, Card, user.id, AccessType.READ)
                if can_write:
                    for user in can_write:
                        MODEL.add_right(new_card.unique_id, Card, user.id, AccessType.WRITE)

                for user in User.objects.all():
                    if user not in can_read and can_read:
                        MODEL.remove_right(new_card.unique_id, Card, user.id, AccessType.READ)
                    if user not in can_write and can_write:
                        MODEL.remove_right(new_card.unique_id, Card, user.id, AccessType.WRITE)

                if interval is not None:
                    interval = datetime.timedelta(seconds=interval)
                    start_repeat_at = form.cleaned_data['start_repeat_at']
                    if start_repeat_at is None:
                        start_repeat_at = datetime.datetime.now() - interval
                    MODEL.plan_write(new_card.unique_id, request.user.id, interval, start_repeat_at)

                return redirect('beb_manager:lists', board_id)
        else:
            form = CardFormWithoutLists(request.user.id, board_id, initial={'priority': Priority.MEDIUM.value})
        editable = bool(MODEL.get_right(list_id, CardsList, request.user.id) & AccessType.WRITE)
        return render(request, 'beb_manager/cards/add.html', {'form': form, 'container_editable': editable})
    except beb_exceptions.AccessDeniedError:
        return HttpResponse('<h1>Access Denied</h1>')


@process_plans
@login_required
def edit_card(request, board_id, card_id):
    try:
        if request.method == 'POST':
            form = CardForm(request.user.id, board_id, request.POST)

            if 'save' in request.POST:
                name = form.data['name']
                if name is None or name == '' or name.isspace():
                    form.add_error('name', "Name should not be empty")

                interval = form.data['interval']
                if interval == '' or interval.isspace():
                    interval = None

                if interval is not None:
                    interval = pytimeparse.parse(interval)
                    if interval is None:
                        form.add_error('interval', "Interval is incorrect")
                    if interval < 300:  # 5 minutes
                        form.add_error('interval', "Interval should be more than 5 minutes")

                if form.is_valid():
                    description = form.cleaned_data['description']
                    tags = []
                    for tag in form.cleaned_data['tags']:
                        try:
                            tags.append(int(tag))
                        except ValueError:
                            pass
                    children_cards = []
                    for card in form.cleaned_data['children_cards']:
                        try:
                            children_cards.append(int(card))
                        except ValueError:
                            pass

                    exp_date = form.cleaned_data['expiration_date']
                    if exp_date is not None:
                        exp_date = exp_date.strftime('%Y-%m-%d %H:%M:%S')

                    card_list = form.cleaned_data['card_list']
                    priority = form.cleaned_data['priority']
                    assignee_user = form.cleaned_data['assignee']
                    assignee = assignee_user.id if assignee_user is not None else None

                    can_read = form.cleaned_data['can_read']
                    can_write = form.cleaned_data['can_write']

                    edited_card = Card(name=name,
                                       unique_id=card_id,
                                       description=description,
                                       assignee_id=assignee,
                                       expiration_date=exp_date,
                                       priority=priority,
                                       tags=tags,
                                       children=children_cards)
                    edited_card = MODEL.card_write(card_list, edited_card, request.user.id)

                    if can_read:
                        for user in can_read:
                            MODEL.add_right(card_id, Card, user.id, AccessType.READ)
                    if can_write:
                        for user in can_write:
                            MODEL.add_right(card_id, Card, user.id, AccessType.WRITE)

                    for user in User.objects.all():
                        if user not in can_read and can_read:
                            MODEL.remove_right(card_id, Card, user.id, AccessType.READ)
                        if user not in can_write and can_write:
                            MODEL.remove_right(card_id, Card, user.id, AccessType.WRITE)

                    if interval is not None:
                        interval = datetime.timedelta(seconds=interval)
                        start_repeat_at = form.cleaned_data['start_repeat_at']
                        if start_repeat_at is not None:
                            start_repeat_at = start_repeat_at.strftime('%Y-%m-%d %H:%M:%S')

                        MODEL.plan_write(edited_card.unique_id, request.user.id, interval, start_repeat_at)
                    elif edited_card.plan is not None:
                        MODEL.plan_delete(edited_card.unique_id, request.user.id)

                    return redirect('beb_manager:lists', board_id)
            elif 'delete' in request.POST:
                print("DELETE")
                MODEL.card_delete(card_id, request_user_id=request.user.id)
                return redirect('beb_manager:lists', board_id)
        else:
            card = MODEL.card_read(None, card_id=card_id, request_user_id=request.user.id)[0]
            list_id = MODEL.get_list_of_card(card.unique_id, request.user.id).unique_id

            if card.plan is not None:
                plan = MODEL.plan_read(card.unique_id, request.user.id)
            else:
                plan = None

            can_write = []
            can_read = []

            for user in User.objects.all():
                print(MODEL.get_right(card_id, Card, user.id))
                if bool(MODEL.get_right(card_id, Card, user.id) & AccessType.READ):
                    can_read.append(user)
                if bool(MODEL.get_right(card_id, Card, user.id) & AccessType.WRITE):
                    can_write.append(user)

            form = CardForm(request.user.id, board_id, initial={
                'name': card.name,
                'description': card.description,
                'tags': card.tags,
                'children_cards': card.children,
                'expiration_date': card.expiration_date,
                'card_list': list_id,
                'priority': card.priority,
                'assignee': User.objects.get(pk=card.assignee_id) if card.assignee_id is not None else None,
                'can_read': can_read,
                'can_write': can_write,
                'interval': plan.interval if plan is not None else None,
            })
            editable = bool(MODEL.get_right(board_id, Board, request.user.id) & AccessType.WRITE)
        return render(request, 'beb_manager/cards/edit.html', {'form': form, 'container_editable': editable})
    except beb_exceptions.AccessDeniedError:
        return HttpResponse('<h1>Access Denied</h1>')


@process_plans
@login_required
def add_tag(request, board_id):
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            color = int('0x' + form.cleaned_data['color'][1:], 16)
            try:
                MODEL.tag_write(tag_name=name, color=color)
            except beb_exceptions.Error:
                pass
            return redirect('beb_manager:lists', board_id)
    else:
        form = TagForm()
    return render(request, 'beb_manager/tags/add.html', {'form': form})


@process_plans
@login_required
def edit_tag(request, tag_id, board_id):
    try:
        tag = MODEL.tag_read(tag_id)[0]
    except beb_exceptions.Error:
        return redirect('beb_manager:lists', board_id)

    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            if 'save' in request.POST:
                new_name = form.cleaned_data['name']
                new_color = int('0x' + form.cleaned_data['color'][1:], 16)

                MODEL.tag_write(tag_id, new_name, new_color)
            elif 'delete' in request.POST:
                MODEL.tag_delete(tag_id)
            return redirect('beb_manager:lists', board_id)
    else:
        form = TagForm(initial={'name': tag.name, 'color': '#{0:06X}'.format(tag.color)})
    return render(request, 'beb_manager/tags/edit.html', {'form': form})


@process_plans
@login_required
def show_tag(request, tag_id, board_id):
    try:
        tag = MODEL.tag_read(tag_id)[0]
        tag.color = '#{0:06X}'.format(tag.color)

        cards = MODEL.card_read(None, board_id=board_id, tag_id=tag_id)
    except beb_exceptions.TagDoesNotExistError:
        return redirect('beb_manager:lists', board_id)
    except beb_exceptions.CardDoesNotExistError:
        cards = []

    return render(request, 'beb_manager/tags/show.html', {'board_id': board_id, 'tag': tag, 'cards': cards})


@process_plans
@login_required
def assigned(request, board_id):
    try:
        cards = MODEL.get_cards_assigned_user(request.user.id, board_id)
    except beb_exceptions.CardDoesNotExistError:
        cards = []

    return render(request, 'beb_manager/cards/sorted.html',
                  {'board_id': board_id, 'cards': cards, 'header_title': "Showing assigned cards"})


@process_plans
@login_required
def owned(request, board_id):
    try:
        cards = MODEL.get_cards_owned_by_user(request.user.id, board_id)
    except beb_exceptions.CardDoesNotExistError:
        cards = []

    return render(request, 'beb_manager/cards/sorted.html',
                  {'board_id': board_id, 'cards': cards, 'header_title': "Showing created cards"})
