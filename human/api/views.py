from django.shortcuts import render

from rest_framework import viewsets, mixins
from .models import User, Query, Response
from .serializers import UserSerializer, QuerySerializer, ResponseSerializer

class CreateListRetrieveDestroyViewSet(mixins.CreateModelMixin,
                                mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                mixins.DestroyModelMixin,
                                viewsets.GenericViewSet):
    """
    A viewset that provides 'retrieve', 'create', 'list', and 'destroy' actions.
    """
    pass


class UserViewSet(CreateListRetrieveDestroyViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class QueryViewSet(CreateListRetrieveDestroyViewSet):
    queryset = Query.objects.all()
    serializer_class = QuerySerializer


class ResponseViewSet(CreateListRetrieveDestroyViewSet):
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer

