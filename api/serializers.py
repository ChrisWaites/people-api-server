from rest_framework import serializers
from django.contrib.auth.models import User

from .models import *
from django.conf import settings

import re

import stripe
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


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
        fields = ('customer_id', 'balance')


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('id', 'transaction_id', 'amount')


class CreateTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('id', 'amount')
        
    def create(self, validated_data):
        amount = validated_data['amount']
        user = validated_data['user']
        if amount >= 0:
            transaction = stripe.Charge.create(
                amount=amount,
                currency='usd',
                customer_id=user.customer_id
            )
            user.balance += amount
            user.save()
            transaction_id = charge.id
        else: # withdraw
            transaction_id = 'withdrawal_test_test'

        return Transaction.objects.create(
            transaction_id=transaction_id,
            **validated_data
        )


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ('id', 'key', 'value')


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

