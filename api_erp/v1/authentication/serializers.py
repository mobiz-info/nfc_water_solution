from __future__ import unicode_literals
import datetime

from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from accounts.models import CustomUser

from six import text_type

class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(UserTokenObtainPairSerializer, cls).get_token(user)
        return token
    
    def validate(cls, attrs):
        data = super(UserTokenObtainPairSerializer, cls).validate(attrs)

        refresh = cls.get_token(cls.user)

        data['refresh'] = text_type(refresh)
        data['access'] = text_type(refresh.access_token)

        if cls.user.is_superuser:
            data['role'] = "superuser"
        else:
            data['role'] = "user"

        return data

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username','password')

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.save()
        return user


class LogInSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()