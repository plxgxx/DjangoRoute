from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def route_filter(request, route_type=None, country=None, location=None):
    print(route_type)
    print(country)
    print(location)
    return HttpResponse('Ok')


def route_detail(request, id):
    print(id)
    return HttpResponse('Ok')


def route_reviews(request, id):
    print(id)
    return HttpResponse('Ok')


def route_add(request):
    return HttpResponse('Ok')


def route_add_event(request, id):
    print(id)
    return HttpResponse('Ok')


def event_handler(request):
    return HttpResponse('Ok!')
