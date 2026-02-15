from datetime import date

from django.shortcuts import render, redirect

from .models import Guest, BreakfastRequest


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
            error = "Código inválido ou fora do período da estadia"

    return render(request, "accounts/login.html", {"error": error})


# -------------------------
# HOME DO HÓSPEDE
# -------------------------
def guest_home(request):
    guest_id = request.session.get("guest_id")
    if not guest_id:
        return redirect("guest_login")

    guest = Guest.objects.get(id=guest_id)
    return render(request, "accounts/home.html", {"guest": guest})


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
