from django.shortcuts import render

from rest_framework import viewsets
from .models import User, Query, Response
from .serializers import UserSerializer, QuerySerializer, ResponseSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class QueryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Query.objects.all()
    serializer_class = QuerySerializer


class ResponseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer

