from django.urls import path
from .views import guest_login, guest_home, breakfast

urlpatterns = [
    path("login/", guest_login, name="guest_login"),
    path("home/", guest_home, name="guest_home"),
    path("breakfast/", breakfast, name="breakfast"),
    path("home/", guest_home, name="home"),
]
