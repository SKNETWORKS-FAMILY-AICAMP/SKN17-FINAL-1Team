from django.urls import path
from . import views

urlpatterns = [
    path("get-hair-images/", views.get_hair_images, name="get_hair_images"),
    path("get-hair-list/", views.get_hair_list, name="get_hair_list"),
]
