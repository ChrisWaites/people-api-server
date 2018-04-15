from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import viewsets, mixins, permissions, response
from rest_framework.decorators import action
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView

from .models import *
from .serializers import *
from .filters import IsOwnerFilterBackend
from .permissions import IsOwnerOrReadOnly

import re
import random
import stripe
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


class UserViewSet(
        mixins.CreateModelMixin,
        viewsets.GenericViewSet
    ):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)


class ProfileViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet
    ):

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    filter_backends = (IsOwnerFilterBackend,)
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)

    def get_serializer_class(self):
        if self.action == 'update':
            return UpdateProfileSerializer
        else:
            return ProfileSerializer


class TransactionViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.CreateModelMixin,
        viewsets.GenericViewSet
    ):

    queryset = Transaction.objects.all()
    filter_backends = (IsOwnerFilterBackend,)
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)

    def perform_create(self, serializer):
        profile = self.request.user.profile
        amount = serializer.validated_data['amount']
        transaction = stripe.Charge.create(
            amount=amount,
            currency='usd',
            customer=profile.customer_id,
        )
        profile.balance += amount # if transaction goes through, safely update balance
        profile.save()
        serializer.save(user=self.request.user, transaction_id=transaction.id)

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateTransactionSerializer
        else:
            return TransactionSerializer


class AttributeViewSet(
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet
    ):

    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer
    filter_backends = (IsOwnerFilterBackend,)
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class QueryViewSet(
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet
    ):

    queryset = Query.objects.all()
    filter_backends = (IsOwnerFilterBackend,)
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)

    @action(detail=False)
    def get(self, request):
        query = random.choice(Query.objects.filter(response=None))
        serializer = self.get_serializer(query)
        return response.Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateQuerySerializer
        elif self.action == 'get':
            return GetQuerySerializer
        else:
            return QuerySerializer


class ResponseViewSet(
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet
    ):

    queryset = Response.objects.all()
    filter_backends = (IsOwnerFilterBackend,)
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateResponseSerializer
        else:
            return ResponseSerializer

