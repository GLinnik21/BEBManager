from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings

from beb_lib.model.model import Model
import beb_lib.model.exceptions as beb_exceptions

from beb_manager.forms import BoardForm

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
        form = BoardForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            try:
                MODEL.board_write(board_name=name,
                                  request_user_id=request.user.id)
            except beb_exceptions.Error:
                pass
            return redirect('beb_manager:boards')
    else:
        form = BoardForm()
    return render(request, 'beb_manager/boards/add.html', {'form': form})


@login_required
def edit_board(request, board_id):
    try:
        board = MODEL.board_read(board_id, request_user_id=request.user.id)[0]
    except beb_exceptions.Error:
        return redirect('beb_manager:boards')

    if request.method == 'POST':
        form = BoardForm(request.POST)
        if form.is_valid():
            new_name = form.cleaned_data['name']
            MODEL.board_write(board.unique_id, new_name, request_user_id=request.user.id)
            return redirect('beb_manager:boards')
    else:
        form = BoardForm(initial={'name': board.name})
    return render(request, 'beb_manager/boards/edit.html', {'form': form})


@login_required
def delete_board(request, board_id):
    if request.method == 'POST':
        MODEL.board_delete(board_id, request_user_id=request.user.id)
    return redirect('beb_manager:boards')
