from django.contrib import admin

from website.models import Screenplay, Breakdown, Message


class ScreenplayAdmin(admin.ModelAdmin):
    readonly_fields = ('created',)

admin.site.register(Screenplay, ScreenplayAdmin)
admin.site.register(Breakdown)
admin.site.register(Message)