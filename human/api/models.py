from django.db import models
import uuid

class User(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return '{}'.format(self.uuid)

class Query(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField()
    regex = models.TextField(default='.*')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return '{}'.format(self.uuid)

class Response(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.ForeignKey(Query, on_delete=models.CASCADE)

    def __str__(self):
        return '{}'.format(self.uuid)

