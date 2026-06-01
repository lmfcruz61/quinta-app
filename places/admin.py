from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Place


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):

    list_display = ("name", "category", "thumbnail_preview", "website_link", "is_active", "order")
    list_filter = ("category", "is_active")
    search_fields = ("name", "description", "website_url")
    ordering = ("order", "name")

    readonly_fields = ("thumbnail_preview", "map_picker")

    fieldsets = (
        (None, {
            "fields": ("name", "category", "description", "website_url", "thumbnail", "thumbnail_preview", "icon", "is_active", "order")
        }),
        ("Localização", {
            "fields": ("latitude", "longitude", "map_picker")
        }),
    )

    def map_picker(self, obj=None):
        return mark_safe("""
            <div style="margin-top:10px;">
              <div style="font-weight:600; margin-bottom:6px;">
                Selecionar localização no mapa
              </div>

              <div id="admin-map" style="
                    width:100%;
                    height:600px;
                    border-radius:12px;
                    border:1px solid #333;">
              </div>

              <div style="margin-top:6px; color:#888; font-size:12px;">
                Clique no mapa ou arraste o marcador para preencher Latitude/Longitude automaticamente.
              </div>
            </div>
        """)

    map_picker.short_description = ""

    def thumbnail_preview(self, obj):
        if not obj or not obj.thumbnail:
            return ""
        return format_html(
            '<img src="{}" alt="{}" style="height: 52px; width: 72px; object-fit: cover; border-radius: 6px;">',
            obj.thumbnail.url,
            obj.name,
        )

    thumbnail_preview.short_description = "thumbnail"

    def website_link(self, obj):
        if not obj.website_url:
            return ""
        return format_html(
            '<a href="{}" target="_blank" rel="noopener">abrir</a>',
            obj.website_url,
        )

    website_link.short_description = "link"

    class Media:
        css = {
            "all": ("https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",)
        }
        js = (
            "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js",
            "places/js/place_map.js",
        )
