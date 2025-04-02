'''
Tests for the user API
'''
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
USER_TOKEN_URL = reverse('user:token')
USER_SELF_URL = reverse('user:me')  # aka User Me URL

'''regular user info'''
_DEFAULT_EMAIL = 'user@example.com'
_DEFAULT_PASSWORD = 'sample123'
_DEFAULT_FIRST_NAME = 'Some'
_DEFAULT_LAST_NAME = 'User'

'''incorrect user info'''
_NONEXISTENT_EMAIL = 'nonexistent_user@example.com'
_NONEXISTENT_PASSWORD = 'sample123'
_SHORT_PASSWORD = '123'


def create_user(**kwargs):
    '''Create and return a new endpoint user'''
    return get_user_model().objects.create_user(**kwargs)


class PublicUserApiTests(TestCase):
    '''Test the public (unauthenticated) features of the endpoint user API'''

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        '''Test that creating an endpoint user is successful'''
        payload = {
            'email': _DEFAULT_EMAIL,
            'password': _DEFAULT_PASSWORD,
            'first_name': _DEFAULT_FIRST_NAME,
            'last_name': _DEFAULT_LAST_NAME,
        }
        result = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', result.data)  # password will not return

    def test_user_with_email_exists(self):
        '''Test error if attempt create endpoint user with email reuse'''
        payload = {
            'email': _DEFAULT_EMAIL,
            'password': _DEFAULT_PASSWORD,
            'first_name': _DEFAULT_FIRST_NAME,
            'last_name': _DEFAULT_LAST_NAME,
        }
        create_user(**payload)

        result = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_with_short_password(self):
        '''Test error if attempt create endpoint user with a short password'''
        payload = {
            'email': _DEFAULT_EMAIL,
            'password': _SHORT_PASSWORD,
            'first_name': _DEFAULT_FIRST_NAME,
            'last_name': _DEFAULT_LAST_NAME,
        }
        result = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        '''Test creation of token for valid endpoint user credential'''
        user_details = {
            'email': _DEFAULT_EMAIL,
            'password': _DEFAULT_PASSWORD,
            'first_name': _DEFAULT_FIRST_NAME,
            'last_name': _DEFAULT_LAST_NAME,
        }
        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        result = self.client.post(USER_TOKEN_URL, payload)

        self.assertIn('token', result.data)
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_attempt_bad_credentials(self):
        '''Test the attempt at creating a token with invalid credentials'''
        payload = {
            'email': _NONEXISTENT_EMAIL,
            'password': _NONEXISTENT_PASSWORD,
        }

        result = self.client.post(USER_TOKEN_URL, payload)

        self.assertNotIn('token', result.data)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_attempt_unauthorized_user_me(self):
        '''
        Test that retrieving the profile of an endpoint user
        without proper authentication is not possible
        '''
        result = self.client.get(USER_SELF_URL)

        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    '''Test the private (authenticated) features of the endpoint user API'''

    def setUp(self):
        payload = {
            'email': _DEFAULT_EMAIL,
            'password': _DEFAULT_PASSWORD,
            'first_name': _DEFAULT_FIRST_NAME,
            'last_name': _DEFAULT_LAST_NAME,
        }
        self.user = create_user(**payload)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    '''This tests a scenario where a user is de-authenticated'''
    def test_retrieve_profile_success(self):
        '''
        Test the retrieval of the profile (user object) of the logged in user
        '''
        result = self.client.get(USER_SELF_URL)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, {
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        })

    def test_post_to_user_profile_not_allowed(self):
        '''Test that POST to the profile of an endpoint user is not possible'''
        result = self.client.post(USER_SELF_URL, {})

        self.assertEqual(
            result.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_patch_to_user_profile(self):
        '''Test updating the endpoint user profile if authenticated'''
        payload = {
            'email': _DEFAULT_EMAIL,
            'password': _DEFAULT_PASSWORD + '_updated',
            'first_name': _DEFAULT_FIRST_NAME + '_updated',
            'last_name': _DEFAULT_LAST_NAME,
        }

        result = self.client.patch(USER_SELF_URL, payload)

        self.user.refresh_from_db()  # odd that user data is not auto refreshed
        self.assertEqual(self.user.first_name, payload['first_name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(result.status_code, status.HTTP_200_OK)
