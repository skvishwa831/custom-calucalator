from django.urls import path

from django.contrib import admin
from . import views
from .views import (
    CalculateView,
    CustomerNamesListView,
    GamesTypesListView,
    MyTokenObtainPairView,
    shutDown,
    record_fetch,
    register,
    CustomLoginView,
    SaveRecords,
    GameDashBoardView,
    GameWinnnigNumbers,
    BakiJamaAmountsView,
    GetJamaBakiRecords,
)
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path("", views.index, name="index"),
    path("calculate/", CalculateView.as_view(), name="calculate"),
    path("shutdown/", shutDown.as_view(), name="shutDown"),
    path("record/", record_fetch.as_view(), name="record"),
    path(
        "fetch_saved_names/",
        views.fetch_saved_Names.as_view(),
        name="fetch_saved_names",
    ),
    path("delete_records/", views.delete_records.as_view(), name="delete_records"),
    path("login/", CustomLoginView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "customer-names/", CustomerNamesListView.as_view(), name="customer-names-list"
    ),
    path("games/", GamesTypesListView.as_view(), name="games-list"),
    path("register/", register, name="register"),
    path("save-record/", SaveRecords.as_view(), name="save-record"),
    path("game-dashboard/", GameDashBoardView.as_view(), name="game-dashboard"),
    path(
        "game-winning-numbers/",
        GameWinnnigNumbers.as_view(),
        name="game-winning-numbers",
    ),
    path("baki-jama/", BakiJamaAmountsView.as_view(), name="baki-jama-list"),
    path("get-jama-baki/", GetJamaBakiRecords.as_view(), name="get-jama-baki-url"),
]
