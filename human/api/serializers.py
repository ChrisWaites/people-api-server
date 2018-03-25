from rest_framework import serializers
from .models import User, Query, Response


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('uuid',)


class QuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Query
        fields = ('uuid', 'text', 'regex', 'user')


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = ('uuid', 'text', 'user', 'query')

