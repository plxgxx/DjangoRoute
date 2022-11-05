import json

from django.contrib.auth import  authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection
from ROUTE import models
from mongo_utils import MongoDBConnection
from bson import ObjectId
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator





# Create your views here.
def route_filter(request, route_type=None, country=None, location=None):
    cursor = connection.cursor()
    query_filter = []
    if route_type is not None:
        query_filter.append(f"route_type='{route_type}'")
    if country is not None:
        query_filter.append(f"country='{country}'")
    if location is not None:
        query_filter.append(f"location='{location}'")


    filter_string = ' and '.join(query_filter)

    joining = """SELECT ROUTE_route.country,
                        ROUTE_route.description,
                        ROUTE_route.duration,
                        ROUTE_route.stopping_point,
                        ROUTE_route.route_type,
                        start_point.name,
                        end_point.name
                 FROM ROUTE_route JOIN 
                 ROUTE_places as start_point 
                 ON start_point.id = ROUTE_route.starting_point
                 JOIN ROUTE_places as end_point 
                 ON end_point.id = ROUTE_route.destination WHERE """ + filter_string

    cursor.execute(joining)

    result = cursor.fetchall()

    new_result = []
    for i in result:
        new_country = i[0]
        new_description = i[1]
        new_duration = i[2]
        new_stopping = i[3]
        new_type = i[4]
        new_start = i[5]
        new_end = i[6]
        result_dict = {"country": new_country,
                       "description": new_description,
                       "duration": new_duration,
                       "stopping_point": new_stopping,
                       "route_type": new_type,
                       "starting_point": new_start,
                       "ending_point": new_end,}
        new_result.append(result_dict)
    if new_result is not None:
        p = Paginator(new_result, 2)
        num_page = int(request.GET.get('page', default=1))
        if num_page < p.num_pages:
            num_page = 1
        select_page = p.get_page(num_page)

        return HttpResponse(select_page.object_list)
    else:
        return HttpResponse("No route found")


def route_detail(request, route_id):
    cursor = connection.cursor()
    join = f"""SELECT ROUTE_route.country,
                        ROUTE_route.description,
                        ROUTE_route.duration,
                        ROUTE_route.stopping_point,
                        ROUTE_route.route_type,
                        start_point.name,
                        end_point.name
                        FROM ROUTE_route
                            JOIN ROUTE_places as start_point
                                ON start_point.id = ROUTE_route.starting_point
                            JOIN route_places as end_point
                                ON end_point.id = ROUTE_route.destination
                            WHERE ROUTE_route.id = '{route_id}' """
    cursor.execute(join)
    result = cursor.fetchall()

    new_result = []
    for i in result:
        new_country = i[0]
        new_description = i[1]
        new_duration = i[2]
        new_stopping = i[3]
        new_type = i[4]
        new_start = i[5]
        new_end = i[6]
        result_dict = {"country": new_country,
                       "description": new_description,
                       "duration": new_duration,
                       "stopping_point": new_stopping,
                       "route_type": new_type,
                       "starting_point": new_start,
                       "ending_point": new_end, }
        new_result.append(result_dict)
    with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
        collec = db['stop_points']
        stop_point = collec.find_one({"_id": ObjectId(new_result[0].get('stopping_point'))})

    showing_result = {"object": new_result, "stopping_point": stop_point}


    return HttpResponse(str(showing_result))


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
            stop_points = request.POST.get('stop_points')
            country = request.POST.get('country')
            location = request.POST.get('location')
            description = request.POST.get('description')
            duration = request.POST.get('duration')
            route_type = request.POST.get('route_type')

            models.validate_stop_point(stop_points)
            stop_list = json.loads(stop_points)

            with MongoDBConnection('admin','admin', '127.0.0.1') as db:
                collec = db['stop_points']
                id_stop_points = collec.insert_one({'points': stop_list}).inserted_id

            start_obj = models.Places.objects.get(name=start_point)
            dest_obj = models.Places.objects.get(name=destination)

            new_route = models.Route(starting_point=start_obj.id, destination=dest_obj.id,
                                     country = country, location=location, description=description,
                                     duration=duration,route_type=route_type, stopping_point=id_stop_points)

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

            new_event = models.Event(id_route=route_id, event_admin=1, event_users=[], start_date=start_date, price=price)
            try:
                new_event.full_clean()
                new_event.save()
                return HttpResponse('Event Added')
            except ValidationError:
                return HttpResponse('Date error')
    else:
        return HttpResponse('No rights')


def event_handler(request, event_id):
    cursor = connection.cursor()

    join = f"""SELECT event.id,
                     event.start_date,
                     event.price,
                     event.event_users,
                     route.country,
                     route.location,
                     route.stopping_point,
                     place.name,
                     route.duration, 
                     route.description
                        FROM ROUTE_event as event
                            JOIN ROUTE_route as route
                                ON event.id_route = route.id
                            JOIN route_places as place
                                ON route.destination = place.id
                            WHERE event.id = '{event_id}' """

    cursor.execute(join)
    result = cursor.fetchall()

    new_result = []
    for i in result:
        new_id = i[0]
        new_date = i[1]
        new_price = i[2]
        new_users = i[3]
        new_country = i[4]
        new_location = i[5]
        new_stopping = i[6]
        new_end = i[7]
        new_duration = i[8]
        new_description = i[9]
        result_dict = {"id": new_id,
                       "date": new_date,
                       "price": new_price,
                       "id_users": new_users,
                       "country": new_country,
                       "location": new_location,
                       "stopping_point": new_stopping,
                       "ending_point": new_end,
                       "duration": new_duration,
                       "description": new_description,
                       }
        new_result.append(result_dict)
    with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
        collec = db['event_users']
        id_users = collec.find_one({"_id": ObjectId(new_result[0].get('id_users'))})

    users_pending = User.objects.filter(pk__in=id_users['pending'])
    users_accepted = User.objects.filter(pk__in=id_users['accepted'])

    list_users_accepted = [{itm.id:itm.username} for itm in users_accepted]
    list_users_pending = [{itm.id:itm.username} for itm in users_pending]
    new_result[0]['accepted users'] = list_users_accepted
    new_result[0]['pending users'] = list_users_pending
    showing_result = {"object": new_result, "users": id_users}


    return HttpResponse(str(showing_result))


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

def add_me_toevent(request, event_id):
    user = request.user.id
    event = models.Event.objects.filter(id=event_id).first()
    with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
        event_users = db['event_users']
        all_event_users = event_users.find_one({'_id': ObjectId(event.event_users)})
        if user in all_event_users['pending'] or user in all_event_users['accepted']:
            return HttpResponse('You are in pending users')
        else:
            all_event_users['pending'].append(user)
            event_users.update_one({'_id': ObjectId(event.event_users)}, {"$set": all_event_users}, upsert=False)

    return HttpResponse('You are accepted')


def event_accept_user(request, event_id):
    if request.method == "GET":
        return render(request, "accept_user.html")
    if request.method == "POST":
        event = models.Event.objects.filter(id=event_id).first()
        accepted = int(request.POST.get('accept'))
        with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
            event_users = db['event_users']
            all_event_users = event_users.find_one({'_id': ObjectId(event.event_users)})
            if accepted in all_event_users['accepted']:
                return HttpResponse('User already accepted')
            else:
                all_event_users['accepted'].append(accepted)
                event_users.update_one({'_id': ObjectId(event.event_users)}, {"$set": all_event_users}, upsert=False)

        return HttpResponse("User accepted to event")