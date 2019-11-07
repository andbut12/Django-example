from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from user.models import User, Group


class UserTests(APITestCase):
    fixtures = ['test']

    def setUp(self):
        self.client = APIClient()
        self.client.login(username='admin@grandclass.net', password='123qwe')

        self.list_url = reverse('api:user-list')
        self.detail_url = reverse('api:user-detail', kwargs={'pk': User.objects.last().id})

    def test_list(self):
        """
        Ensure we can get user objects.
        """
        response = self.client.get(self.list_url)

        self.assertContains(response, 'Teacher')

    def test_detail(self):
        """
        Ensure we can get user details.
        """
        response = self.client.get(self.detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
