from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse

from rest_framework import viewsets, mixins, permissions, response
from rest_framework.decorators import action
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from .models import *
from .serializers import *
from .filters import IsOwnerFilterBackend
from .permissions import IsOwnerOrReadOnly

import random
import stripe
import requests

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeRegisterView(APIView):

    def get(self, request):
        print(request.__dict__)
        req = requests.get('https://connect.stripe.com/express/oauth/authorize',
            params = {
                'client_id': settings.STRIPE_CLIENT_ID,
                'redirect_uri': settings.STRIPE_REDIRECT_URI
            }
        )
        return redirect(req.url)

    def post(self, request):
        print(request.__dict__)
        resp = requests.post('https://connect.stripe.com/oauth/token', data={
            'client_secret': settings.STRIPE_SECRET_KEY,
            'code': request.data['code'],
            'grant_type': 'authorization_code',
        })
        print(resp)


class UserViewSet(
        mixins.CreateModelMixin,
        viewsets.GenericViewSet
    ):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)


class ProfileView(APIView):

    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)

    def get(self, request):
        return response.Response({'balance': Profile.objects.get(user=request.user).balance()})


class CheckoutView(APIView):

    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request):
        return response.Response({
            'amount': request.query_params['amount'],
            'stripePublicKey': settings.STRIPE_PUBLIC_KEY,
        }, template_name='checkout.html')


class DepositViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.CreateModelMixin,
        viewsets.GenericViewSet
    ):

    queryset = Deposit.objects.all()
    filter_backends = (IsOwnerFilterBackend,)
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)

    def perform_create(self, serializer):
        amount = serializer.validated_data['amount']

        charge = stripe.Charge.create(
            amount=amount,
            currency='usd',
            source=serializer.validated_data['stripeToken'],
        )

        serializer.save(user=self.request.user, chargeId=charge.id)

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateDepositSerializer
        else:
            return DepositSerializer


class PayoutViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.CreateModelMixin,
        viewsets.GenericViewSet
    ):

    queryset = Payout.objects.all()
    filter_backends = (IsOwnerFilterBackend,)
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)

    def perform_create(self, serializer):
        amount = serializer.validated_data['amount']

        if self.request.user.profile.balance() < amount:
            raise ValidationError('Insufficient balance.')

        payout = stripe.Payout.create(
            amount=amount,
            currency='usd',
            destination=serializer.validated_data['stripeAccountId'],
        )

        serializer.save(user=self.request.user, payoutId=payout.id)

    def get_serializer_class(self):
        if self.action == 'create':
            return CreatePayoutSerializer
        else:
            return PayoutSerializer


class AttributeViewSet(
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
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
        bid = serializer.validated_data.get('bid', 1)
        if self.request.user.profile.balance() < bid:
            raise ValidationError('Insufficient balance.')
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

class RatingViewSet(
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet
    ):

    queryset = Rating.objects.all()
    filter_backends = (IsOwnerFilterBackend,)
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateRatingSerializer
        else:
            return RatingSerializer

