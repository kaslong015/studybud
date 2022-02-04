from unicodedata import name
from django import http
import django
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import *
from .forms import *
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
# Create your views here.


def LoginPage(request):

    page = 'login'

    if request.user.is_authenticated:
        return redirect('/')

    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'user does not exist')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'invalid details')
    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def registerPage(request):

    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            messages.success(request, 'Account created successfully')
            return redirect('/')
        else:
            messages.error(request, 'form is invalid')
    context = {'form': form}
    return render(request, 'base/login_register.html', context)


def LogoutPage(request):
    logout(request)
    return redirect('/')


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(description__icontains=q) |
        Q(name__icontains=q) |
        Q(host__username__icontains=q)
    )

    topics = Topic.objects.all()
    room_count = rooms.count()

    context = {"rooms": rooms, 'topics': topics, 'room_count': room_count}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    context = {'room': room,'room_messages':room_messages}
    return render(request, 'base/room.html', context)


@login_required(login_url='/login/')
def createRoom(request):
    form = RoomForm()

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    context = {'form': form}
    return render(request, 'base/form_room.html', context)


@login_required(login_url='/login/')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return redirect('/')

    form = RoomForm(instance=room)
    context = {'form': form}

    return render(request, 'base/form_room.html', context)


def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return redirect('/')

    if request.method == 'POST':
        room.delete()
        return redirect('/')
    return render(request, 'base/delete.html', {'obj': room})
