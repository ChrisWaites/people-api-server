from rest_framework import serializers
from django.contrib.auth.models import User

import re

from .models import *


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password')

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username']
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class CreatePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('id', 'token', 'queries')

    def validate(self, data):
        if len(data['queries']) < 50:
            raise serializers.ValidationError('Payment must be at least 50 cents.')
        return data

    def create(self, validated_data):
        charge = stripe.Charge.create(
            amount=len(self.queries),
            currency='usd',
            source=self.token,
        )
        return Payment.objects.create(stripe_id=charge.id, **validated_data)


class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = '__all__'


class CreateTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = ('id', 'token', 'responses')

    def validate(self, data):
        if len(data['responses']) < 50:
            raise serializers.ValidationError('Transfer must be at least 50 cents.')
        return data

    def create(self, validated_data):
        transfer = stripe.Transfer.create(
            amount=len(self.responses),
            currency='usd',
            destination=self.account_id,
        )
        return Transfer.objects.create(stripe_id=transfer.id, **validated_data)


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

