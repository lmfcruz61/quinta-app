from django.urls import path
from .views import guest_login, guest_home, breakfast, chat, menu

urlpatterns = [
    path("", guest_login, name="guest_login_root"),
    path("login/", guest_login, name="guest_login"),
    path("home/", guest_home, name="guest_home"),
    path("chat/", chat, name="chat"),
    path("breakfast/", breakfast, name="breakfast"),
    path("menu/", menu, name="menu"),
    path("home/", guest_home, name="home"),
]
