from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_views
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

from datetime import datetime
import math
import random
import requests
import stripe


stripe.api_key = settings.STRIPE_SECRET_KEY

class SocialLoginView(auth_views.LoginView):
    redirect_field_name = 'redirect_uri'
    
    #def get_redirect_url(self):
    #    return self.request.POST.get('redirect_uri')


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
        profile = Profile.objects.get(user=request.user)
        return response.Response({
            'stripeAccountId': profile.stripeAccountId,
            'balance': profile.balance()
        })


class DepositView(APIView):

    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request):
        return response.Response({
            'email': request.user.email,
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

        stripe_fees = math.ceil((amount * 0.029) + 30)
        internal_fees = math.ceil(amount * 0.01)
        amount_post_fees = amount - stripe_fees - internal_fees

        if amount <= 50 or amount_post_fees <= 0:
            raise Exception('Deposit amount too small.')

        charge = stripe.Charge.create(
            amount=amount,
            currency='usd',
            source=serializer.validated_data['stripeToken'],
            stripe_account=self.request.user.profile.stripeAccountId,
        )

        serializer.save(amount=amount_post_fees, user=self.request.user, id=charge.id)

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateDepositSerializer
        else:
            return DepositSerializer


class RegisterView(APIView):

    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)

    def get(self, request):
        if 'code' not in request.query_params:
            return redirect('https://connect.stripe.com/express/oauth/authorize?client_id={}&stripe_user[email]={}'.format(
                settings.STRIPE_CLIENT_ID,
                request.user.email,
            ))

        else: 
            resp = requests.post('https://connect.stripe.com/oauth/token', data={
                'client_secret': settings.STRIPE_SECRET_KEY,
                'code': request.query_params['code'],
                'grant_type': 'authorization_code',
            })

            request.user.profile.stripeAccountId = resp.json()['stripe_user_id']
            request.user.profile.save()

            return redirect('/')


class TransferViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.CreateModelMixin,
        viewsets.GenericViewSet
    ):

    queryset = Transfer.objects.all()
    filter_backends = (IsOwnerFilterBackend,)
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)

    def perform_create(self, serializer):
        amount = serializer.validated_data['amount']
        user = self.request.user

        if self.request.user.profile.balance() < amount:
            raise ValidationError('Insufficient balance.')

        transfer = stripe.Transfer.create(
            amount=amount,
            currency='usd',
            destination=user.profile.stripeAccountId,
        )

        serializer.save(user=user, id=transfer.id)

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateTransferSerializer
        else:
            return TransferSerializer


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

        query.numRetrievals += 1
        query.lastRetrieved = datetime.now()
        query.save()

        return response.Response(self.get_serializer(query).data)

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
        try:
            url = serializer.validated_data['query'].callback
            if url != None:
                resp = requests.post(url, data=serializer.validated_data)
        except:
            pass

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

