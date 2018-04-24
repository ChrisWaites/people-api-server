from rest_framework import serializers
from django.contrib.auth.models import User

from .models import *
from django.conf import settings

import re


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password')

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = '__all__'


class CreateDepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = ('id', 'stripeToken', 'amount')


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = '__all__'


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = '__all__'


class CreateResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = ('id', 'text', 'query')

    def validate(self, data):
        text = data['text']
        regex = data['query'].regex
        if not re.fullmatch(regex, text):
            raise serializers.ValidationError('Response text \'{}\' does not match query regex r\'{}\''.format(text, regex))
        return data


class QuerySerializer(serializers.ModelSerializer):
    response = ResponseSerializer(read_only=True)

    class Meta:
        model = Query
        fields = '__all__'


class CreateQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Query
        fields = ('id', 'text', 'regex')


class GetQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Query
        fields = ('id', 'text', 'regex')

