from django.db import models
from django.utils.translation import gettext_lazy


# Create your models here.

class Choice(models.Model):
    choice_text = models.CharField(max_length=200)
    votes = models.ImageField(default=0)


class Places(models.Model):
    name = models.CharField(max_length=50)


class Route(models.Model):
    starting_point = models.IntegerField()
    stopping_point = models.JSONField()
    destination = models.IntegerField()
    country = models.CharField(max_length=50)
    location = models.CharField(max_length=50)
    description = models.TextField()

    class RouteType(models.TextChoices):
        Car = 'Car', gettext_lazy('Car')
        ByFoot = 'Foot', gettext_lazy('Foot')

    route_type = models.CharField(
        max_length=50,
        choices=RouteType.choices,
        default=RouteType.ByFoot
    )
    duration = models.IntegerField()


class Event(models.Model):
    id_route = models.IntegerField()
    event_admin = models.IntegerField()
    approved_user = models.JSONField()
    pending_users = models.CharField(max_length=50)
    start_date = models.DateField()
    price = models.IntegerField()
