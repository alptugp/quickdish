from django.urls import path

from . import views

urlpatterns = [
    # ex: /drpapp/ - the index page
    path("", views.index, name="index"),
    # ex: /drpapp/comparison/ - the price comparison page
    path("comparison/", views.comparison, name="comparison"),
]
