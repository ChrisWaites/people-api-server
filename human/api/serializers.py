from rest_framework import serializers
import re

from .models import *


class QuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Query
        fields = ('id', 'text', 'regex', 'response', 'created')

class CreateQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Query
        fields = ('text', 'regex')

class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = ('id', 'text', 'query', 'created')

class CreateResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = ('text', 'query')

    def validate(self, data):
        text = data['text']
        regex = data['query'].regex
        if not re.fullmatch(regex, text):
            raise serializers.ValidationError('Response text \'{}\' does not match query regex r\'{}\''.format(text, regex))
        return data

