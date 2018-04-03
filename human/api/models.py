from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
    """
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """
    https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
    """
    instance.profile.save()


class Query(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    regex = models.TextField(default='.*')
    created = models.DateTimeField(auto_now_add=True)


class Response(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    query = models.ForeignKey(Query, related_name='responses', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)


class Attribute(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.TextField()
    value = models.TextField()

