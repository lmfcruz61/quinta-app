from django.db import models


class Room(models.Model):
    number = models.CharField(max_length=10)
    name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.number
