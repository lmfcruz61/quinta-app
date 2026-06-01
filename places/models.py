from django.core.validators import FileExtensionValidator
from django.db import models


class Place(models.Model):

    CATEGORY_CHOICES = [
        ('monument', 'Monumento'),
        ('restaurant', 'Restaurante'),
        ('interest', 'Ponto de Interesse'),
        ('beach', 'Praia'),
        ('supermarket', 'Supermercado'),
    ]

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    description = models.TextField(blank=True)
    website_url = models.URLField("link da página", blank=True)
    thumbnail = models.FileField(
        "thumbnail",
        upload_to="places/",
        blank=True,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])],
    )

    latitude = models.FloatField()
    longitude = models.FloatField()

    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Nome do ícone"
    )

    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "local"
        verbose_name_plural = "Locais"

    def __str__(self):
        return self.name
