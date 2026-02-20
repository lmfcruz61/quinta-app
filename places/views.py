from django.shortcuts import render
from django.conf import settings
from .models import Place

def map_view(request):
    places = Place.objects.filter(is_active=True)

    return render(request, "places/map.html", {
        "places": places,
        "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
    })