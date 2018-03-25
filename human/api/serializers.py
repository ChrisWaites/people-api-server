from rest_framework import serializers
from .models import User, Question, Response


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('uuid',)


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('uuid', 'text', 'regex', 'user')


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = ('uuid', 'text', 'user', 'question')

