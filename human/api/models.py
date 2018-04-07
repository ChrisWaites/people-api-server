from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

import uuid


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.TextField()
    stripe_id = models.TextField()


class Transfer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.TextField()
    stripe_id = models.TextField()


class Query(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, null=True, related_name='queries', on_delete=models.CASCADE)
    text = models.TextField()
    regex = models.TextField(default=r'^.*$')


class Response(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transfer = models.ForeignKey(Transfer, null=True, related_name='responses', on_delete=models.CASCADE)
    text = models.TextField()
    query = models.OneToOneField(Query, related_name='response', on_delete=models.CASCADE)

