from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('room/<str:pk>/', room, name='room'),
    path('create_room/', createRoom, name='create_room'),
    path('update_room/<str:pk>/', updateRoom, name='update_room'),
    path('delete_room/<str:pk>/', deleteRoom, name='delete_room'),
    path('profile/<str:pk>/', userProfile, name='user-profile'),
    path('delete_message/<str:pk>/', deleteMessage, name='delete-message'),
    path('login/', LoginPage, name='login'),
    path('logout/', LogoutPage, name='logout'),
    path('register/', registerPage, name='register'),
]
