from django.urls import path

from . import views

app_name = 'solire'
urlpatterns = [
    path("", views.index, name="index"),

]
