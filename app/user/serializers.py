'''
Serializers for the user API view
'''
from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext_lazy as translate

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    '''Serializer for the endpoint user object'''

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        '''Create and return an endpoint user with a hashed password'''
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        '''Update and return endpoint user without a password'''
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    '''Serializer for the authentication token of the endpoint user '''
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_style': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attributes):
        '''Validate and authenticate the endpoint user'''
        email = attributes.get('email')
        password = attributes.get('password')
        # I do not understand this part, it is not recursive...
        # is it calling a different model?
        user = authenticate(
            request=self.context.get('request'),  # weird requirement
            username=email,
            password=password,
        )
        if not user:
            msg = translate('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authorization')

        attributes['user'] = user
        return attributes
