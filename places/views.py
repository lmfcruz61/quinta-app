from django.shortcuts import render
from django.conf import settings
from .models import Place

def map_view(request):
    places = Place.objects.filter(is_active=True)
    places_data = []

    for place in places:
        places_data.append({
            "id": place.id,
            "name": place.name,
            "description": place.description,
            "latitude": place.latitude,
            "longitude": place.longitude,
            "thumbnail_url": place.thumbnail.url if place.thumbnail else "",
        })

    return render(request, "places/map.html", {
        "places": places,
        "places_data": places_data,
        "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
    })
