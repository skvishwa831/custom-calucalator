from rest_framework import serializers
from .models import (
    Contact,
    CustomerNames,
    GameRecords,
    GamesTypes,
    GameDashBoard,
    GameWinningNumbersRecord,
    BakiJamaAmounts
)


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"


class CustomerNamesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerNames
        fields = ["id", "name"]


class GamesTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GamesTypes
        fields = ["id", "gameName"]


class GameRecordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameRecords
        fields = ["id", "name", "gameName", "content", "date"]


class GameDashBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameDashBoard
        fields = ["id", "name", "totalAmount", "date"]


class GameWinningNumbersRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameWinningNumbersRecord
        fields = ["id", "date", "records"]


class BakiJamaAmountsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BakiJamaAmounts
        fields = ["id", "name", "type", "amount", "date"]
