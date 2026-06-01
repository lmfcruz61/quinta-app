from django.db import models


class Room(models.Model):
    number = models.CharField(max_length=10)
    name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name or self.number


class ICalSync(models.Model):
    name = models.CharField("nome", max_length=120)
    room = models.ForeignKey(Room, verbose_name="quarto", on_delete=models.CASCADE)
    feed_url = models.URLField("link iCal")
    is_active = models.BooleanField("ativo", default=True)
    last_sync_at = models.DateTimeField("última sincronização", blank=True, null=True)
    last_error = models.TextField("último erro", blank=True)
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        ordering = ("room", "name")
        verbose_name = "sincronização iCal"
        verbose_name_plural = "sincronizações iCal"

    def __str__(self):
        return f"{self.name} - {self.room}"


class Reservation(models.Model):
    STATUS_CHOICES = [
        ("confirmed", "Confirmada"),
        ("cancelled", "Cancelada"),
        ("unknown", "Desconhecida"),
    ]

    sync = models.ForeignKey(
        ICalSync,
        verbose_name="sincronização",
        related_name="reservations",
        on_delete=models.CASCADE,
    )
    room = models.ForeignKey(Room, verbose_name="quarto", on_delete=models.CASCADE)
    external_uid = models.CharField("referência iCal", max_length=255)
    title = models.CharField("título", max_length=255, blank=True)
    guest_name = models.CharField("nome do hóspede", max_length=200, blank=True)
    check_in = models.DateField("entrada")
    check_out = models.DateField("saída")
    status = models.CharField("estado", max_length=20, choices=STATUS_CHOICES, default="confirmed")
    raw_summary = models.CharField("resumo original", max_length=255, blank=True)
    raw_description = models.TextField("descrição original", blank=True)
    last_seen_at = models.DateTimeField("vista na última sincronização", blank=True, null=True)
    created_at = models.DateTimeField("criada em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizada em", auto_now=True)

    class Meta:
        ordering = ("check_in", "room")
        unique_together = ("sync", "external_uid")
        verbose_name = "reserva"
        verbose_name_plural = "reservas"

    def __str__(self):
        return f"{self.room} - {self.check_in:%d/%m/%Y} a {self.check_out:%d/%m/%Y}"
