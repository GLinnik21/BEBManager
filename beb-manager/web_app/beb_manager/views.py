import beb_lib.model.exceptions as beb_exceptions
from beb_lib.model.model import Model
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.shortcuts import render, redirect

from beb_manager.forms import SingleInputForm

MODEL = Model(settings.BEB_LIB_DATABASE_PATH)


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


@login_required
def boards(request):
    try:
        beb_boards = MODEL.board_read(request_user_id=request.user.id)
    except beb_exceptions.Error:
        beb_boards = []

    return render(request, 'beb_manager/boards/boards.html', {'user_boards': beb_boards})


@login_required
def add_board(request):
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
    return render(request, 'beb_manager/boards/add.html', {'form': form})


@login_required
def edit_board(request, board_id):
    try:
        board = MODEL.board_read(board_id, request_user_id=request.user.id)[0]
    except beb_exceptions.Error:
        return redirect('beb_manager:boards')

    if request.method == 'POST':
        form = SingleInputForm(request.POST)
        if form.is_valid():
            new_name = form.cleaned_data['name']
            MODEL.board_write(board.unique_id, new_name, request_user_id=request.user.id)
            return redirect('beb_manager:boards')
    else:
        form = SingleInputForm(initial={'name': board.name})
    return render(request, 'beb_manager/boards/edit.html', {'form': form})


@login_required
def delete_board(request, board_id):
    if request.method == 'POST':
        MODEL.board_delete(board_id, request_user_id=request.user.id)
    return redirect('beb_manager:boards')


@login_required
def lists(request, board_id):
    try:
        lists_models = MODEL.list_read(board_id, request_user_id=request.user.id)
        beb_lists = []
        for card_list in lists_models:
            cards = []
            try:
                cards = MODEL.card_read(card_list.unique_id, request_user_id=request.user.id)
            except beb_exceptions.CardDoesNotExistError:
                pass

            beb_lists.append({'list': card_list, 'cards': cards})
        return render(request, 'beb_manager/lists/lists.html',
                      {'beb_lists': beb_lists, 'board_id': board_id})

    except beb_exceptions.Error:
        return redirect('beb_manager:boards')


@login_required
def add_list(request, board_id):
    if request.method == 'POST':
        form = SingleInputForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            try:
                MODEL.list_write(board_id, list_name=name,
                                 request_user_id=request.user.id)
            except beb_exceptions.Error:
                pass
            return redirect('beb_manager:lists', board_id)
    else:
        form = SingleInputForm()
    return render(request, 'beb_manager/lists/add.html', {'form': form})


@login_required
def delete_list(request, board_id, list_id):
    print(list_id)
    if request.method == 'POST':
        MODEL.list_delete(list_id, request_user_id=request.user.id)
    return redirect('beb_manager:lists', board_id)


@login_required
def edit_list(request, board_id, list_id):
    try:
        card_list = MODEL.list_read(None, list_id, request_user_id=request.user.id)[0]
    except beb_exceptions.Error:
        return redirect('beb_manager:lists', board_id)

    if request.method == 'POST':
        form = SingleInputForm(request.POST)
        if form.is_valid():
            new_name = form.cleaned_data['name']
            MODEL.list_write(board_id, list_id, new_name, request.user.id)
            return redirect('beb_manager:lists', board_id)
    else:
        form = SingleInputForm(initial={'name': card_list.name})
    return render(request, 'beb_manager/lists/edit.html', {'form': form})
