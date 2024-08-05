from django.contrib.auth import authenticate
from rest_framework import serializers
from .utils import send_registration_email
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'convoyName', 'phoneNumber', 'profilePicture')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'password2', 'convoyName', 'phoneNumber', 'profilePicture')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords must match."'})
        return attrs

    def validate_email(self, value):
        if not value.endswith('@gmail.com'):
            raise serializers.ValidationError('The email must end with @gmail.com.')
        return value

    def create(self, validated_data):
        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            convoyName=validated_data['convoyName'],
            phoneNumber=validated_data['phoneNumber'],
            profilePicture=validated_data['profilePicture'],
        )
        user.set_password(validated_data['password'])
        user.save()
        send_registration_email(user)
        return user


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'password')

    def validate(self, attrs):
        username = attrs['username']
        password = attrs['password']

        if username and password:
            user = authenticate(request=self.context.get('request'), username=username, password=password)
            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')

        else:
            msg = 'Must include "username" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'convoyName', 'phoneNumber', 'profilePicture')
        read_only_fields = ('id', 'username', 'email')
