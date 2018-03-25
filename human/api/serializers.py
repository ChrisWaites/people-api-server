from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('uuid', 'user')

    # https://medium.freecodecamp.org/nested-relationships-in-serializers-for-onetoone-fields-in-django-rest-framework-bdb4720d81e6
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        profile, created = Profile.objects.update_or_create(user=user, subject_major=validated_data.pop('subject_major'))
        return profile


class QuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Query
        fields = ('uuid', 'text', 'regex', 'profile')


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = ('uuid', 'text', 'profile', 'query')

