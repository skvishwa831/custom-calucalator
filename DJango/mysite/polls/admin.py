from django.contrib import admin

from .models import Contact, User, CustomerNames, GamesTypes, GameRecords, GameDashBoard

# Register your models here.

admin.site.register(Contact)
admin.site.register(User)
admin.site.register(GamesTypes)
admin.site.register(CustomerNames)
admin.site.register(GameRecords)
admin.site.register(GameDashBoard)