from django.conf import settings

from django.db import models


class Notification(models.Model):
    text = models.CharField(max_length=500)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sent = models.BooleanField(default=False)
