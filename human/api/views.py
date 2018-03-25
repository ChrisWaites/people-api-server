from django.shortcuts import render

from rest_framework import viewsets, mixins
from .models import Profile, Query, Response
from .serializers import ProfileSerializer, QuerySerializer, ResponseSerializer

class CreateListRetrieveDestroyViewSet(mixins.CreateModelMixin,
                                mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                mixins.DestroyModelMixin,
                                viewsets.GenericViewSet):
    """
    A viewset that provides 'retrieve', 'create', 'list', and 'destroy' actions.
    """
    pass


class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class QueryViewSet(CreateListRetrieveDestroyViewSet):
    queryset = Query.objects.all()
    serializer_class = QuerySerializer


class ResponseViewSet(CreateListRetrieveDestroyViewSet):
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer

