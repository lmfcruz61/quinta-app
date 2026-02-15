from django.db import models
from django.contrib.auth.models import User
from rooms.models import Room
import uuid
from datetime import date


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
        return (
            self.is_active and
            self.check_in <= today <= self.check_out
        )

    def __str__(self):
        return f"{self.user.username} - {self.room}"

class BreakfastRequest(models.Model):
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.guest} - {self.date} {self.time}"
