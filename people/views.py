from django.conf import settings
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
from pymessenger import bot
import random
import requests
import stripe

import uuid


stripe.api_key = settings.STRIPE_SECRET_KEY
bot = bot.Bot(settings.ACCESS_TOKEN)


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


class MessengerLoginView(auth_views.LoginView):
    def get_success_url(self):
        return self.request.GET.get('redirect_uri') + '&authorization_code=' + str(self.request.user.profile.id)


class MessengerRegisterView(auth_views.LoginView):
    def get_success_url(self):
        return 'https://people-api-server.herokuapp.com/register'


class MessengerView(APIView):
    def get(self, request):
        token_sent = request.query_params.get("hub.verify_token")
        if token_sent == settings.VERIFY_TOKEN:
            return HttpResponse(request.query_params.get("hub.challenge"))
        return HttpResponse('Invalid verification token.')

    def post(self, request):
        try:
            for event in request.data.get('entry'):
                messaging = event.get('messaging')
                for message in messaging:

                    sender_id = message.get('sender').get('id')

                    if message.get('message'):

                        text = message.get('message').get('text')

                        responded_to_query = False
                        # See if the sender is a logged in user and, if so, has a current query to be answered
                        try:
                            profile = Profile.objects.get(messengerId=sender_id)
                            query = Query.objects.get(id=profile.currentQueryId)
                            Response.objects.create(user=profile.user, query=query, text=text)

                            profile.currentQueryId = None
                            profile.save()

                            bot.send_text_message(sender_id, "Thanks! You've been credited {} cents.".format(query.bid))
                            responded_to_query = True
                        except Exception as e:
                            pass

                        if responded_to_query:
                            pass

                        elif text == 'help':
                            bot.send_text_message(sender_id, 'Hello! Try sending some of the following to interact with our system.\n\nregister\nlogin\nlogout\nget')
                            
                        elif text == 'register':
                            bot.send_button_message(
                                sender_id, 'Click here to register.', [{
                                        'type': 'web_url',
                                        'url': 'https://people-api-server.herokuapp.com/messenger-register/',
                                        'title': 'Register',
                                    }]
                                )

                        elif text == 'login':
                            bot.send_button_message(
                                sender_id, 'Welcome! Click here to login.', [{
                                        'type': 'account_link',
                                        'url': 'https://people-api-server.herokuapp.com/messenger-login/',
                                    }]
                                )

                        elif text == 'logout':
                            bot.send_button_message(
                                sender_id, 'Sorry to see you go! Click here to logout.', [{
                                        'type': 'account_unlink'
                                    }]
                                )

                        elif text == 'get':
                            query = random.choice(Query.objects.filter(response=None))

                            profile = Profile.objects.get(messengerId=sender_id)
                            profile.currentQueryId = query.id
                            profile.save()

                            bot.send_text_message(sender_id, 'Here you go {}.\n\n{}'.format(profile.user.username, query.text))

                        else:
                            bot.send_text_message(sender_id, "Sorry, didn't quite understand that.")

                    elif message.get('account_linking'):
                        if message.get('account_linking').get('status') == 'linked':

                            auth_code = message.get('account_linking').get('authorization_code')

                            profile = Profile.objects.get(id=auth_code)
                            profile.messengerId = sender_id
                            profile.save()

                            bot.send_text_message(sender_id, 'Welcome {}!'.format(profile.user.username))

                        else:

                            profile = Profile.objects.get(messengerId=sender_id)
                            profile.messengerId = None
                            profile.save()

        except Exception as e:
            print(e)

        return HttpResponse('Message processed.')

