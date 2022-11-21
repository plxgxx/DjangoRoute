from django.test import TestCase, Client
from ROUTE.models import Route, Event
# Create your tests here.


class TestRoute(TestCase):

    def setUp(self):
        self.route = Route(starting_point=1, stopping_point='[{"name": "test", "lat":1, "lon":1}]',
                           destination=2, country='test', location='test', description='test', route_type='Car',
                           duration=4)
        self.route.save()

    def test_get_route_filter(self):
        client = Client()
        response = client.get('/ROUTE/Car/test/test')
        self.assertEqual(200, response.status_code)


class TestEvent(TestCase):

    def test_anonym_user(self):
        client = Client()
        response = client.get('/ROUTE/1/add_event')
        self.assertEqual(200, response.status_code)

        response = client.post('/ROUTE/1/add_event')
        self.assertEqual(200, response.status_code)

class TestRouteFixture(TestCase):
    fixtures = ['route.json']

    def test_recieving(self):
        resp = self.client.get('/ROUTE/event_review/1')
        parsed_resp = resp.json()
        self.assertEqual('1st one', parsed_resp[0]['description'])
        print(parsed_resp)