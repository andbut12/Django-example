from django.test import TestCase

from user.models import User, Group


class UserModelTest(TestCase):
    fixtures = ['test']

    def test_string_representation(self):
        """
        Ensure __str__ is working
        """
        user = User.objects.first()
        self.assertEqual(str(user), '({}) - {} - {}'.format(user.site.domain, user.email, user.full_name))

    def test_short_name(self):
        """
        Ensure we can get_short_name
        """
        user = User.objects.first()
        self.assertEqual(User.get_short_name(user), user.short_name)

    def test_full_name(self):
        """
        Ensure we can get_full_name
        """
        user = User.objects.first()
        self.assertEqual(User.get_full_name(user), user.full_name)

    def test_organization(self):
        """
        Ensure we can organization
        """
        user = User.objects.first()
        self.assertEqual(user.organization, user.site.organization)


class GroupModelTest(TestCase):
    fixtures = ['test']

    def test_string_representation(self):
        """
        Ensure __str__ is working
        """
        group = Group.objects.create(site_id=1, title='title')
        self.assertEqual(str(group), group.title)
