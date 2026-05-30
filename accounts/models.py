from datetime import date
from decimal import Decimal
import uuid

from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models

from rooms.models import Room


class Guest(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)

    check_in = models.DateField()
    check_out = models.DateField()

    access_code = models.CharField(max_length=8, unique=True, editable=False)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.access_code:
            self.access_code = uuid.uuid4().hex[:6].upper()
        super().save(*args, **kwargs)

    def is_valid_now(self):
        today = date.today()
        return self.is_active and self.check_in <= today <= self.check_out

    def __str__(self):
        return f"{self.user.username} - {self.room}"


class BreakfastRequest(models.Model):
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.guest} - {self.date} {self.time}"


class ChatMessage(models.Model):
    SENDER_CHOICES = [
        ("guest", "Hóspede"),
        ("staff", "Equipa"),
    ]

    guest = models.ForeignKey(Guest, related_name="chat_messages", on_delete=models.CASCADE)
    sender = models.CharField("remetente", max_length=10, choices=SENDER_CHOICES)
    message = models.TextField("mensagem")
    is_read = models.BooleanField("lida", default=False)
    created_at = models.DateTimeField("criada em", auto_now_add=True)

    class Meta:
        ordering = ("created_at",)
        verbose_name = "mensagem de chat"
        verbose_name_plural = "chat"

    def __str__(self):
        return f"{self.get_sender_display()} - {self.guest} - {self.created_at:%d/%m/%Y %H:%M}"


class MenuItem(models.Model):
    CATEGORY_CHOICES = [
        ("starter", "Entrada"),
        ("main", "Prato principal"),
        ("dessert", "Sobremesa"),
        ("drink", "Bebida"),
        ("other", "Outro"),
    ]

    category = models.CharField(
        "categoria",
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="main",
    )
    name = models.CharField("nome", max_length=120)
    description = models.TextField("descrição", blank=True)
    photo = models.FileField(
        "foto",
        upload_to="menu_items/",
        blank=True,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])],
    )
    price = models.DecimalField("preço", max_digits=6, decimal_places=2, blank=True, null=True)
    is_available = models.BooleanField("disponível", default=True)
    order = models.PositiveIntegerField("ordem", default=0)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        ordering = ("category", "order", "name")
        verbose_name = "item da ementa"
        verbose_name_plural = "ementa"

    def __str__(self):
        return self.name


class MenuOrder(models.Model):
    STATUS_CHOICES = [
        ("new", "Nova"),
        ("preparing", "Em preparação"),
        ("delivered", "Entregue"),
        ("cancelled", "Cancelada"),
    ]

    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    status = models.CharField("estado", max_length=20, choices=STATUS_CHOICES, default="new")
    notes = models.TextField("observações", blank=True)
    created_at = models.DateTimeField("criada em", auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "encomenda"
        verbose_name_plural = "encomendas"

    @property
    def total(self):
        return sum((item.total for item in self.items.all()), Decimal("0.00"))

    def __str__(self):
        return f"Encomenda #{self.id} - {self.guest}"


class MenuOrderItem(models.Model):
    order = models.ForeignKey(MenuOrder, related_name="items", on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, verbose_name="prato", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField("quantidade")
    unit_price = models.DecimalField("preço unitário", max_digits=6, decimal_places=2, default=0)

    class Meta:
        verbose_name = "item da encomenda"
        verbose_name_plural = "itens da encomenda"

    @property
    def total(self):
        if not self.quantity:
            return Decimal("0.00")
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"
