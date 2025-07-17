from django.urls import path

from django.contrib import admin
from . import views
from .views import CalculateView, shutDown, record_fetch

urlpatterns = [
    path("", views.index, name="index"),
    path("calculate/", CalculateView.as_view(), name="calculate"),
    path("shutdown/", shutDown.as_view(), name="shutDown"),
    path("record/", record_fetch.as_view(), name="record"),
]
