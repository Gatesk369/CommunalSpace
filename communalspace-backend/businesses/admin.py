from django.contrib import admin

from .models import Business, BusinessBranch, BusinessOwnerHistory

admin.site.register(Business)
admin.site.register(BusinessBranch)
admin.site.register(BusinessOwnerHistory)
