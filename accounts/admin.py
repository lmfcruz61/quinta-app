from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from .models import ChatMessage, Guest, BreakfastRequest, MenuItem, MenuOrder, MenuOrderItem


admin.site.index_template = "admin/dashboard.html"

original_each_context = admin.site.each_context


def admin_each_context(request):
    context = original_each_context(request)
    today = timezone.localdate()
    context["admin_notifications"] = {
        "unread_messages": ChatMessage.objects.filter(sender="guest", is_read=False).count(),
        "new_orders": MenuOrder.objects.filter(status="new").count(),
        "breakfast_today": BreakfastRequest.objects.filter(date=today).count(),
        "chat_url": f"{reverse('admin:accounts_chatmessage_changelist')}?sender__exact=guest&is_read__exact=0",
        "orders_url": f"{reverse('admin:accounts_menuorder_changelist')}?status__exact=new",
        "breakfast_url": reverse("admin:accounts_breakfastrequest_changelist"),
    }
    return context


admin.site.each_context = admin_each_context


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


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    change_list_template = "admin/accounts/chatmessage/change_list.html"
    list_display = ("guest", "sender", "read_status", "short_message", "created_at")
    list_filter = ("sender", "is_read", "created_at")
    search_fields = (
        "guest__user__username",
        "guest__user__first_name",
        "guest__user__last_name",
        "guest__access_code",
        "message",
    )
    ordering = ("-created_at",)
    fields = ("guest", "sender", "message", "is_read", "created_at")
    readonly_fields = ("created_at",)
    actions = ("mark_as_read",)

    def short_message(self, obj):
        return obj.message[:80]

    short_message.short_description = "mensagem"

    def read_status(self, obj):
        if obj.sender == "staff":
            return "-"
        return "sim" if obj.is_read else "não"

    read_status.short_description = "lida"

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} mensagem(ns) marcada(s) como lida(s).")

    mark_as_read.short_description = "Marcar como lida"


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "photo_preview", "price", "is_available", "order", "updated_at")
    list_editable = ("category", "price", "is_available", "order")
    list_filter = ("category", "is_available")
    search_fields = ("name", "description")
    ordering = ("category", "order", "name")
    readonly_fields = ("photo_preview",)
    fields = ("category", "name", "description", "photo", "photo_preview", "price", "is_available", "order")

    def photo_preview(self, obj):
        if not obj.photo:
            return ""
        return format_html(
            '<img src="{}" alt="{}" style="height: 48px; width: 64px; object-fit: cover; border-radius: 6px;">',
            obj.photo.url,
            obj.name,
        )

    photo_preview.short_description = "foto"


class MenuOrderItemInline(admin.TabularInline):
    model = MenuOrderItem
    extra = 0
    readonly_fields = ("menu_item", "quantity", "unit_price", "line_total")
    can_delete = False

    def line_total(self, obj):
        if not obj.pk:
            return ""
        return obj.total

    line_total.short_description = "total"


@admin.register(MenuOrder)
class MenuOrderAdmin(admin.ModelAdmin):
    change_form_template = "admin/accounts/menuorder/change_form.html"
    list_display = ("id", "guest", "status", "total_display", "created_at")
    list_editable = ("status",)
    list_filter = ("status", "created_at")
    search_fields = (
        "guest__user__username",
        "guest__user__first_name",
        "guest__user__last_name",
        "guest__access_code",
    )
    readonly_fields = ("guest", "notes", "created_at", "total_display")
    inlines = (MenuOrderItemInline,)
    ordering = ("-created_at",)

    def total_display(self, obj):
        return obj.total

    total_display.short_description = "total"
