from django.shortcuts import render
from rest_framework import viewsets, mixins, permissions

from .models import *
from .serializers import *
from .filters import IsOwnerFilterBackend
from .permissions import IsOwnerOrReadOnly


class CreateListRetrieveDestroyViewSet(mixins.CreateModelMixin,
                                mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                mixins.DestroyModelMixin,
                                viewsets.GenericViewSet):
    """
    A viewset that provides 'retrieve', 'create', 'list', and 'destroy' actions.
    """
    pass


class UpdateListRetrieveViewSet(mixins.UpdateModelMixin,
                                mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):
    """
    A viewset that provides 'update', 'list', and 'retrieve' actions.
    """
    pass


class ProfileViewSet(UpdateListRetrieveViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    filter_backends = (IsOwnerFilterBackend,)
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class QueryViewSet(CreateListRetrieveDestroyViewSet):
    queryset = Query.objects.all()
    serializer_class = QuerySerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ResponseViewSet(CreateListRetrieveDestroyViewSet):
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AttributeViewSet(CreateListRetrieveDestroyViewSet):
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RatingViewSet(CreateListRetrieveDestroyViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
