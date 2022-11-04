from django.urls import path

from . import views

app_name = 'ROUTE'

urlpatterns = [
    path('', views.route_filter, name='index'),
    path('add_route', views.route_add, name="add_route"),
    path('event_review/<int:event_id>', views.event_handler, name="event_review"),
    path('event_review/<int:event_id>/add_me', views.add_me_toevent, name='add_me'),
    path('event_review/<int:event_id>/accept_user', views.event_accept_user, name='accept_user'),
    path('<int:route_id>', views.route_detail, name='route'),
    path('<int:route_id>/add_event', views.route_add_event, name='route_add_event'),
    path('<str:route_type>', views.route_filter, name='route_type'),
    path('<str:route_type>/<str:country>', views.route_filter, name='route_country'),
    path('<str:route_type>/<str:country>/<str:location>', views.route_filter, name='route_location'),
    path('<int:route_id>/reviews', views.route_reviews, name='route_reviews'),


]