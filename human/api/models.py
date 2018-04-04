from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Query(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    regex = models.TextField(default=r'^.*$')
    created = models.DateTimeField(auto_now_add=True)


class Response(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    query = models.OneToOneField(Query, related_name='response', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

