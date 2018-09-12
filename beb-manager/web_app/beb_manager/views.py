from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings

from beb_lib.model.model import Model
import beb_lib.model.exceptions as beb_lib_exceptions


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
    model = Model(settings.BEB_LIB_DATABASE_PATH)
    try:
        beb_boards = model.board_read(request_user_id=request.user.id)
    except beb_lib_exceptions.Error:
        beb_boards = []

    return render(request, 'beb_manager/boards.html', {'user_boards': beb_boards})
