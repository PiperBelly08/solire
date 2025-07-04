from django.urls import path

from . import views

app_name = 'solire_app'
urlpatterns = [
    path("", views.index, name="index"),
    path("api/insert/", views.insert_data, name="insert_data"),
    path("api/", views.list_data, name="list_data"),
    path("api/clear/", views.clear_data, name="clear_data"),
]
