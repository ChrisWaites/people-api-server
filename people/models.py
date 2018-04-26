from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

import uuid


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile', primary_key=True, on_delete=models.CASCADE)
    stripeAccountId = models.TextField(default='')

    def balance(self):
        deposits = Deposit.objects.filter(user=self.user).aggregate(value=models.Sum('amount'))['value']
        deposits = deposits if deposits != None else 0

        payouts = Payout.objects.filter(user=self.user).aggregate(value=models.Sum('amount'))['value']
        payouts = payouts if payouts != None else 0

        responses = Response.objects.filter(user=self.user).aggregate(value=models.Sum('query__bid'))['value']
        responses = responses if responses != None else 0

        queries = Query.objects.filter(user=self.user).aggregate(value=models.Sum('bid'))['value']
        queries = queries if queries != None else 0

        return deposits + responses - payouts - queries


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html
    """
    instance.profile.save()


class Deposit(models.Model):
    chargeId = models.TextField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stripeToken = models.TextField()
    amount = models.PositiveIntegerField()


class Payout(models.Model):
    payoutId = models.TextField(primary_key=True)
    stripeAccountId = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()


class Attribute(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.TextField()
    value = models.TextField()


class Query(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    regex = models.TextField(default=r'.*')
    bid = models.PositiveIntegerField(default=1)


class Response(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    query = models.OneToOneField(Query, related_name='response', on_delete=models.CASCADE)


class Rating(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    satisfactory = models.BooleanField(default=True)
    response = models.OneToOneField(Response, related_name='rating', on_delete=models.CASCADE)

