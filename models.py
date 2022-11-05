import datetime

from django.db import models
from django.utils.translation import gettext_lazy
import json
from  django.core.exceptions import ValidationError


# Create your models here.

class Choice(models.Model):
    choice_text = models.CharField(max_length=200)
    votes = models.ImageField(default=0)


class Places(models.Model):
    name = models.CharField(max_length=50)

def validate_stop_point(value):
    try:
        stoping_validate = json.loads(value)
        for itm in stoping_validate:
            if 'name' in itm and 'lat' in itm and 'lon' in itm:
                continue
            else:
                raise ValidationError('Error')
    except:
        raise ValidationError('Form is not json')


def validate_route_type(value):
        if value not in ['Car', 'Foot', 'Bike']:
            raise ValidationError('ERROR')

class Route(models.Model):
    starting_point = models.IntegerField()
    stopping_point = models.CharField(max_length=50, validators=[validate_stop_point])
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

def validation_date(value):
    try:
        parsed_date = value
    except:
        raise ValidationError('ERROR')
    if datetime.date.today() > parsed_date:
        raise ValidationError('ERROR')


class Event(models.Model):
    id_route = models.IntegerField()
    event_admin = models.IntegerField()
    event_users = models.CharField(max_length=50)
    start_date = models.DateField(validators=[validation_date])
    price = models.IntegerField()


