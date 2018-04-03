from rest_framework import serializers

from .models import *


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id',)


class QuerySerializer(serializers.ModelSerializer):
    responses = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Query
        fields = ('id', 'text', 'regex', 'responses')


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = ('id', 'text', 'query')


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ('id', 'key', 'value')

