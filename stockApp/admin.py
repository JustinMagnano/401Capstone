from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Stock)
admin.site.register(Portfolio)
admin.site.register(Transaction)
admin.site.register(Account)
admin.site.register(Holidays)
admin.site.register(MarketHours)
admin.site.register(MarketDay)
admin.site.register(ContactMessage)
