'''
Tests for models
'''
from django.test import TestCase
from django.contrib.auth import get_user_model


_DEFAULT_PASSWORD = 'sample123'
_DEFAULT_EMAIL = 'test@example.com'


class ModelTests(TestCase):
    '''Test models'''

    def test_create_user_with_email_successful(self):
        '''Test that creating a user with an email is successful'''
        email = _DEFAULT_EMAIL
        password = _DEFAULT_PASSWORD
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        '''Test email is normalized for new users'''
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(
                email,
                _DEFAULT_PASSWORD
            )
            self.assertEquals(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        '''
        Test that creating a user without an email address raises ValueError
        '''
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', _DEFAULT_PASSWORD)

    def test_create_super_user(self):
        '''Test the happy path of superuser creation'''
        user = get_user_model().objects.create_superuser(
            _DEFAULT_EMAIL,
            _DEFAULT_PASSWORD
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
