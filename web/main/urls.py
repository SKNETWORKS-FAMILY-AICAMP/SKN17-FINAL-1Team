from django.urls import path
from main import views

app_name = 'main'

urlpatterns = [
    path('',views.main_view, name='main'),
    path('gallery/', views.gallery, name='gallery'),
    path('gallery/upload', views.gallery_upload, name='gallery_upload'),
    path('gallery/delete', views.gallery_delete, name='gallery_delete'),
    path('gallery/<int:image_id>/', views.gallery_image_url, name='gallery_image_url'),
    path('gallery/copy-profile', views.copy_profile_to_gallery, name='copy_profile_to_gallery'),
    path('chat/list', views.chat_list, name='chat_list'),
    path('chat/create', views.chat_create, name='chat_create'),
    path('chat/<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('chat/<int:chat_id>/update', views.chat_update, name='chat_update'),
    path('chat/<int:chat_id>/delete', views.chat_delete, name='chat_delete'),
    path('chat/<int:chat_id>/check-complete', views.check_response_complete, name='check_response_complete'),
    path('message/save', views.message_save, name='message_save'),
    path('message/response/', views.message_response, name='message_response'),
]
