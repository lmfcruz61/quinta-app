from django.contrib import admin
from django.utils.safestring import mark_safe
from django.conf import settings
from .models import Place


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):

    list_display = ("name", "category", "is_active", "order")
    list_filter = ("category", "is_active")
    search_fields = ("name", "description")
    ordering = ("order", "name")

    readonly_fields = ("map_picker",)   # ⭐ CRÍTICO

    fieldsets = (
        (None, {
            "fields": ("name", "category", "description", "icon", "is_active", "order")
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
                Clique no mapa para preencher Latitude/Longitude automaticamente.
              </div>
            </div>
        """)

    map_picker.short_description = ""

    class Media:
       js = (
        "https://maps.googleapis.com/maps/api/js?key=" + settings.GOOGLE_MAPS_API_KEY,
        "places/js/place_map.js",
    )