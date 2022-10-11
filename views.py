from django.contrib.auth import  authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse
from ROUTE import models


# Create your views here.
def route_filter(request, route_type=None, country=None, location=None):
    query_filter = {}
    if route_type is not None:
        query_filter['route_type'] = route_type
    if country is not None:
        query_filter['country'] = country
    if route_type is not None:
        query_filter['location'] = location

    result = models.Route.objects.all().filter(**query_filter)
    return HttpResponse([{'country':itm.country, 'id':itm.id} for itm in result])


def route_detail(request, id):
    result = models.Route.objects.all().filter(id=id)
    return HttpResponse([{'country': itm.country, 'id': itm.id}for itm in result])


def route_reviews(request, route_id):
    result = models.Route.objects.all().filter(route_id=route_id)
    return HttpResponse([{'id_route':itm.id_route, 'start_date': itm.start_date,
                          'price': itm.price}for itm in result])


def route_add(request):
    if request.user.has_perm('route.add_route'):
        if request.method == 'GET':
            return render(request, 'add_route.html')

        if request.method == 'POST':
            destination = request.POST.get('destination')
            start_point = request.POST.get('starting_point')
            country = request.POST.get('country')
            location = request.POST.get('location')
            description = request.POST.get('description')
            duration = request.POST.get('duration')
            route_type = request.POST.get('route_type')

            start_obj = models.Places.objects.get(name=start_point)
            dest_obj = models.Places.objects.get(name=destination)

            new_route = models.Route(starting_point=start_obj.id, destination=dest_obj.id,
                                     country = country, location=location, description=description,
                                     duration=duration,route_type=route_type, stopping_point={})
            new_route.save()
            return HttpResponse('Route created')
    else:
        return HttpResponse('No rights')


def route_add_event(request, route_id):
    if request.user.has_perm('route.add_event'):
        if request.method == 'GET':
            return render(request, 'add_event_route.html')

        if request.method == 'POST':
            start_date = request.POST.get('start_date')
            price = request.POST.get('price')

            new_event = models.Event(id_route=route_id, event_admin=1,approved_user=[],
                                     pending_users=[], start_date=start_date, price=price)
            new_event.save()
        return HttpResponse('Event Added')
    else:
        return HttpResponse('No rights')


def event_handler(request, event_id):
    result = models.Event.objects.all().filter(id=event_id)
    return HttpResponse([{'id_route': itm.id_route, 'start_date': itm.start_date,
                          'price': itm.price}for itm in result])


def user_login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    if request.method == 'POST':
        usernm = request.POST['username']
        passwrd = request.POST['password']
        user = authenticate(username=usernm, password=passwrd)
        if user is not None:
            login(request, user)
            return HttpResponse('Successful login')
        else:
            return HttpResponse('No such registered user')


def user_registration(request):
    if request.method == 'GET':
        return render(request, 'registration.html')
    if request.method == 'POST':
        user = User.objects.create_user(username=request.POST.get('username'),
                                        email=request.POST.get('email'),
                                        password=request.POST.get('password'),
                                        first_name=request.POST.get('first'),
                                        last_name=request.POST.get('last'))
        user.save()
        return HttpResponse('User is created')


def logout_user(request):
    logout(request)
    print(request.user.has_perm('route.event'))
    return redirect('/login')