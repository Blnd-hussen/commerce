from django.contrib import admin

from .models import *
# Register your models here.

admin.site.register(Auction)
admin.site.register(Item)
admin.site.register(Category)
admin.site.register(User)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Watchlist)

