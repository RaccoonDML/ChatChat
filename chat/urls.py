#-*- coding:utf-8 -*-
from django.urls import path
from  chat import  views

urlpatterns = [
    path('', views.index, name='index'),
    path('chat/', views.dashboard, name='chat_dashboard'),
    path('msg_send/',views.send_msg,name='send_msg' ),
    path('new_msgs/',views.get_new_msgs,name='get_new_msgs' ),
    path('file_upload/',views.file_upload,name='file_uploads' ),
    path('login/', views.user_login_view, name='login'),
    path('logout/',views.user_logout_view, name='logout'),
    path('vedio-chat/', views.vedio_chat, name='vedio_chat')
]
