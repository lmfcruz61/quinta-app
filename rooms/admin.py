from datetime import datetime
from urllib.error import URLError
from urllib.request import Request, urlopen

from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import ICalSync, Reservation, Room


admin.site.site_header = "Quinta da Ponte Administration"
admin.site.site_title = "Quinta da Ponte Admin"
admin.site.index_title = "Gestão da Quinta da Ponte"


def unfold_ical_lines(content):
    lines = content.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    unfolded = []

    for line in lines:
        if not line:
            continue
        if line.startswith((" ", "\t")) and unfolded:
            unfolded[-1] += line[1:]
        else:
            unfolded.append(line)

    return unfolded


def parse_ical_value(line):
    if ":" not in line:
        return "", ""
    key, value = line.split(":", 1)
    key = key.split(";", 1)[0].upper()
    return key, value.strip()


def parse_ical_date(value):
    value = value.strip()
    if "T" in value:
        value = value.split("T", 1)[0]
    return datetime.strptime(value[:8], "%Y%m%d").date()


def parse_ical_events(content):
    events = []
    current = None

    for line in unfold_ical_lines(content):
        if line == "BEGIN:VEVENT":
            current = {}
            continue
        if line == "END:VEVENT":
            if current:
                events.append(current)
            current = None
            continue
        if current is None:
            continue

        key, value = parse_ical_value(line)
        if key:
            current[key] = value

    return events


def sync_ical_feed(sync):
    request = Request(
        sync.feed_url,
        headers={"User-Agent": "Quinta da Ponte reservations sync"},
    )

    with urlopen(request, timeout=30) as response:
        content = response.read().decode("utf-8", errors="replace")

    now = timezone.now()
    created = 0
    updated = 0
    skipped = 0

    for event in parse_ical_events(content):
        uid = event.get("UID") or event.get("URL")
        starts_at = event.get("DTSTART")
        ends_at = event.get("DTEND")

        if not uid or not starts_at or not ends_at:
            skipped += 1
            continue

        summary = event.get("SUMMARY", "")
        status_value = event.get("STATUS", "").upper()
        status = "cancelled" if status_value == "CANCELLED" else "confirmed"

        _, was_created = Reservation.objects.update_or_create(
            sync=sync,
            external_uid=uid,
            defaults={
                "room": sync.room,
                "title": summary,
                "guest_name": summary,
                "check_in": parse_ical_date(starts_at),
                "check_out": parse_ical_date(ends_at),
                "status": status,
                "raw_summary": summary,
                "raw_description": event.get("DESCRIPTION", ""),
                "last_seen_at": now,
            },
        )

        if was_created:
            created += 1
        else:
            updated += 1

    sync.last_sync_at = now
    sync.last_error = ""
    sync.save(update_fields=("last_sync_at", "last_error", "updated_at"))

    return created, updated, skipped


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("number", "name")
    search_fields = ("number", "name")


@admin.register(ICalSync)
class ICalSyncAdmin(admin.ModelAdmin):
    list_display = ("name", "room", "is_active", "last_sync_at", "reservations_count", "last_error_short")
    list_filter = ("is_active", "room")
    search_fields = ("name", "room__name", "room__number", "feed_url")
    fields = ("name", "room", "feed_url", "is_active", "last_sync_at", "last_error")
    readonly_fields = ("last_sync_at", "last_error")
    actions = ("sync_selected",)

    def reservations_count(self, obj):
        return obj.reservations.count()

    reservations_count.short_description = "reservas"

    def last_error_short(self, obj):
        if not obj.last_error:
            return ""
        return obj.last_error[:80]

    last_error_short.short_description = "erro"

    def sync_selected(self, request, queryset):
        total_created = 0
        total_updated = 0
        total_skipped = 0
        failed = 0

        for sync in queryset:
            if not sync.is_active:
                continue
            try:
                created, updated, skipped = sync_ical_feed(sync)
                total_created += created
                total_updated += updated
                total_skipped += skipped
            except (URLError, TimeoutError, ValueError, OSError) as exc:
                failed += 1
                sync.last_error = str(exc)
                sync.save(update_fields=("last_error", "updated_at"))

        self.message_user(
            request,
            (
                f"Sincronizacao concluida: {total_created} criada(s), "
                f"{total_updated} atualizada(s), {total_skipped} ignorada(s), "
                f"{failed} com erro."
            ),
        )

    sync_selected.short_description = "Sincronizar reservas selecionadas"


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("room", "date_range", "guest_display", "status", "sync", "last_seen_at")
    list_filter = ("status", "room", "sync", "check_in")
    search_fields = ("title", "guest_name", "external_uid", "raw_summary", "raw_description")
    readonly_fields = (
        "sync",
        "room",
        "external_uid",
        "title",
        "guest_name",
        "check_in",
        "check_out",
        "status",
        "raw_summary",
        "raw_description",
        "last_seen_at",
        "created_at",
        "updated_at",
    )
    fields = readonly_fields
    ordering = ("check_in", "room")

    def date_range(self, obj):
        return f"{obj.check_in:%d/%m/%Y} - {obj.check_out:%d/%m/%Y}"

    date_range.short_description = "datas"

    def guest_display(self, obj):
        if not obj.guest_name:
            return "-"
        return format_html("<strong>{}</strong>", obj.guest_name)

    guest_display.short_description = "hospede"
