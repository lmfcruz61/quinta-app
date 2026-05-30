from datetime import date

from django.shortcuts import render, redirect
from django.utils.translation import gettext as _

from .models import ChatMessage, Guest, BreakfastRequest, MenuItem, MenuOrder, MenuOrderItem


# -------------------------
# LOGIN DO HÓSPEDE
# -------------------------
def guest_login(request):
    error = None

    if request.method == "POST":
        code = request.POST.get("code", "").upper()

        try:
            # procurar hóspede pelo código
            guest = Guest.objects.get(access_code=code)

            # validar se o acesso é válido (ativo + datas)
            if not guest.is_valid_now():
                raise Guest.DoesNotExist

            # guardar sessão
            request.session["guest_id"] = guest.id
            return redirect("guest_home")

        except Guest.DoesNotExist:
            error = _("Código inválido ou fora do período da estadia")

    return render(request, "accounts/login.html", {"error": error})


# -------------------------
# HOME DO HÓSPEDE
# -------------------------
def guest_home(request):
    guest_id = request.session.get("guest_id")
    if not guest_id:
        return redirect("guest_login")

    guest = Guest.objects.get(id=guest_id)
    guest_name = guest.user.get_full_name() or guest.user.username
    room_name = guest.room.name if guest.room and guest.room.name else guest.room

    return render(
        request,
        "accounts/home.html",
        {
            "guest": guest,
            "guest_name": guest_name,
            "room_name": room_name,
        }
    )


# -------------------------
# PEQUENO-ALMOÇO
# -------------------------
def breakfast(request):
    guest_id = request.session.get("guest_id")
    if not guest_id:
        return redirect("guest_login")

    guest = Guest.objects.get(id=guest_id)
    today = date.today()

    # buscar pedido existente (se houver)
    breakfast_request = BreakfastRequest.objects.filter(
        guest=guest,
        date=today
    ).first()

    if request.method == "POST":
        time = request.POST.get("time")

        if breakfast_request:
            # atualizar hora
            breakfast_request.time = time
            breakfast_request.save()
        else:
            # criar novo pedido
            BreakfastRequest.objects.create(
                guest=guest,
                date=today,
                time=time
            )

        return redirect("breakfast")

    times = ["08:00", "08:30", "09:00", "09:30", "10:00"]

    return render(
        request,
        "accounts/breakfast.html",
        {
            "guest": guest,
            "times": times,
            "breakfast_request": breakfast_request,
        }
    )


def chat(request):
    guest_id = request.session.get("guest_id")
    if not guest_id:
        return redirect("guest_login")

    guest = Guest.objects.get(id=guest_id)
    error = None

    if request.method == "POST":
        message = request.POST.get("message", "").strip()
        if message:
            ChatMessage.objects.create(
                guest=guest,
                sender="guest",
                message=message,
            )
            return redirect("chat")
        error = _("Escreva uma mensagem antes de enviar.")

    messages = ChatMessage.objects.filter(guest=guest)

    return render(
        request,
        "accounts/chat.html",
        {
            "guest": guest,
            "messages": messages,
            "error": error,
        }
    )


def menu(request):
    guest_id = request.session.get("guest_id")
    if not guest_id:
        return redirect("guest_login")

    guest = Guest.objects.get(id=guest_id)
    items = MenuItem.objects.filter(is_available=True)
    success = False
    error = None

    if request.method == "POST":
        selected_items = []

        for item in items:
            try:
                quantity = int(request.POST.get(f"quantity_{item.id}", 0))
            except (TypeError, ValueError):
                quantity = 0

            if quantity > 0:
                selected_items.append((item, quantity))

        if selected_items:
            order = MenuOrder.objects.create(
                guest=guest,
                notes=request.POST.get("notes", "").strip(),
            )

            for item, quantity in selected_items:
                MenuOrderItem.objects.create(
                    order=order,
                    menu_item=item,
                    quantity=quantity,
                    unit_price=item.price or 0,
                )

            success = True
        else:
            error = _("Selecione pelo menos um prato.")

    categories = []
    for value, label in MenuItem.CATEGORY_CHOICES:
        category_items = [item for item in items if item.category == value]
        if category_items:
            categories.append({"label": _(label), "items": category_items})

    return render(
        request,
        "accounts/menu.html",
        {
            "guest": guest,
            "categories": categories,
            "success": success,
            "error": error,
        }
    )
