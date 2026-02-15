from django.contrib import admin
from .models import Room

admin.site.site_header = "Quinta da Ponte Administration"
admin.site.site_title = "Quinta da Ponte Admin"
admin.site.index_title = "Gestão da Quinta da Ponte"

admin.site.register(Room)
