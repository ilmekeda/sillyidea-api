'''
Tests for th eDjango Admin modifications
'''
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


'''super user info'''
_DEFAULT_EMAIL1 = 'admin@example.com'
_DEFAULT_PASSWORD1 = 'sample123'
_DEFAULT_FIRST_NAME1 = 'Some'
_DEFAULT_LAST_NAME1 = 'Admin'


'''regular user info'''
_DEFAULT_EMAIL2 = 'user@example.com'
_DEFAULT_PASSWORD2 = 'sample123'
_DEFAULT_FIRST_NAME2 = 'Some'
_DEFAULT_LAST_NAME2 = 'User'


class AdminSiteTests(TestCase):
    '''Tests for Django admin ui and etc'''

    def setUp(self):
        '''Create user and client'''
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email=_DEFAULT_EMAIL1,
            password=_DEFAULT_PASSWORD1,
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email=_DEFAULT_EMAIL2,
            password=_DEFAULT_PASSWORD2,
            first_name=_DEFAULT_FIRST_NAME2,
            last_name=_DEFAULT_LAST_NAME2,
        )

    def test_users_list(self):
        '''Test that users are presented, at least in json'''
        url = reverse('admin:core_user_changelist')
        result = self.client.get(url)

        self.assertContains(result, self.user.last_name)
        self.assertContains(result, self.user.first_name)
        self.assertContains(result, self.user.email)

    def test_edit_user_page(self):
        '''Test to make sure that the edit use page works in admin'''
        url = reverse('admin:core_user_change', args=[self.user.id])
        result = self.client.get(url)

        self.assertEqual(result.status_code, 200)

    def test_create_user_page(self):
        '''Test that the create user page works in admin'''
        url = reverse('admin:core_user_add')
        result = self.client.get(url)

        self.assertEqual(result.status_code, 200)
