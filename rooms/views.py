from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .models import Place


def map_view(request):
    places = Place.objects.filter(is_active=True)
    return render(request, "places/map.html", {"places": places})
