from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .service import get_sentiment

import uuid 


class Tweet(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    category        = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True)
    id              = models.UUIDField(default = uuid.uuid4, primary_key=True, editable = False)
    tid             = models.CharField(max_length=100)
    username        = models.CharField(max_length=500, blank=True, null=True)
    tweet           = models.CharField(max_length=500, blank=True, null=True)
    text            = models.CharField(max_length=500, blank=True, null=True)
    likes           = models.IntegerField(default=0)
    timestamp       = models.DateTimeField(blank=True, null=True)
    remark          = models.CharField(max_length=500, blank=True, null=True)

    score           = models.IntegerField(default=0)
    is_negative     = models.BooleanField(default=False)
    is_reviewd      = models.BooleanField(default=False)
    is_emergency    = models.BooleanField(default=False)

    is_testing_record = models.BooleanField(default=False)


    created         = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return str(self.user) + ' - ' + str(self.id)

    class Meta:
        ordering = ['-created']


# @receiver(post_save, sender=Tweet)
# def update_score(sender, instance, created, **kwargs):
#     if created:
#         instance.score = get_sentiment(instance.text)


class Category(models.Model):
    name    = models.CharField(max_length=100)
    slug    = models.SlugField(max_length=100)

    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    