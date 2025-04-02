'''
Database Models
'''
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import gettext_lazy as translate


def update_last_login(sender, user, **kwargs):
    '''
    A signal receiver which updates the last_login date for
    the user logging in.
    '''
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])


class UserManager(BaseUserManager):
    '''Manager for a user model'''

    def create_user(self, email, password=None, **extra_fields):
        '''
        Create, save, and return a new user.
        NOTE: a password with none is for testing or user that cannot login
        '''
        if not email:
            raise ValueError('User must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        '''Create, save, and return a new superuser'''
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    '''
    User in this system using custom model with
    admin-compliant permissions
    '''
    email = models.EmailField(
        translate('email address'),
        max_length=255,
        unique=True,
        error_messages={
            'unique': translate('A user with that email already exists.'),
        },
    )
    first_name = models.CharField(translate('first name'), max_length=125)
    last_name = models.CharField(translate('last name'), max_length=125)
    is_active = models.BooleanField(
        default=True,
        help_text=translate(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    is_staff = models.BooleanField(
        translate('staff status'),
        default=False,
        help_text=translate(
            'Designates whether the user can '
            'log into this admin site.'),
    )
    date_joined = models.DateTimeField(
        translate('date joined'),
        default=timezone.now
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = translate('user')
        verbose_name_plural = translate('users')

    def get_full_name(self):
        '''
        Return the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''Return the short name for the user'''
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''Send an email to this user'''
        send_mail(subject, message, from_email, [self.email], **kwargs)
