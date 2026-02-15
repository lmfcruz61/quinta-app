from django.contrib import admin
from .models import Guest, BreakfastRequest


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "room",
        "access_code",
        "check_in",
        "check_out",
        "is_active",
    )

    readonly_fields = ("access_code",)

    list_filter = ("room", "is_active")
    search_fields = ("user__username", "access_code")


@admin.register(BreakfastRequest)
class BreakfastRequestAdmin(admin.ModelAdmin):
    list_display = ("guest", "date", "time")
    list_filter = ("date",)
    ordering = ("date", "time")
