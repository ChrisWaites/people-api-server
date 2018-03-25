from django.shortcuts import render

from rest_framework import viewsets
from .models import User, Question, Response
from .serializers import UserSerializer, QuestionSerializer, ResponseSerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class ResponseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer

