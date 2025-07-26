# chat/urls.py

from django.urls import path
from . import views

app_name = 'cs'
urlpatterns = [
    path('start/', views.start_chat, name='start_chat'),
    path('chats/', views.chat_list, name='chat_list'),
    path('chat/<int:chat_id>/', views.chat_detail, name='chat_detail'),
]
