from django.contrib import admin

from .models import Community, CommunityAdminApplication

admin.site.register(Community)
admin.site.register(CommunityAdminApplication)
