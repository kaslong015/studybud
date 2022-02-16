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

    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()

    room_message = Message.objects.filter(Q(
        room__topic__name__icontains=q)).order_by('-created')

    context = {"rooms": rooms, 'topics': topics, 'room_count': room_count,
               'room_message': room_message}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')

    participants = room.participants.all()

    if request.method == "POST":
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('/room/' + str(pk))

    context = {'room': room, 'room_messages': room_messages,
               'participants': participants}
    return render(request, 'base/room.html', context)


@login_required(login_url='/login/')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )

        return redirect('/')
    context = {'form': form, 'topics': topics}
    return render(request, 'base/form_room.html', context)


@login_required(login_url='/login/')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return redirect('/')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/form_room.html', context)


@login_required(login_url='/login/')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return redirect('/')

    if request.method == 'POST':
        room.delete()
        return redirect('/')
    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='/login/')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return redirect('/')

    if request.method == 'POST':
        message.delete()
        return redirect('/')
    return render(request, 'base/delete.html', {'obj': message})


@login_required(login_url='/login/')
def userProfile(request, pk):

    # get user with id
    user = User.objects.get(id=pk)

    # get all room for user with pk
    rooms = user.room_set.all()

    # get all topics
    topics = Topic.objects.all()

    context = {'user': user, 'rooms': rooms, 'topics': topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url='/login/')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    context = {'form': form}
    return render(request, 'base/update-user.html', context)


def topicPage(request):

    q = request.GET.get('q') if request.GET.get('q') != None else ''

    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})


def activityPage(request):
    room_message = Message.objects.all()
    return render(request,'base/activity.html',{'room_message':room_message})