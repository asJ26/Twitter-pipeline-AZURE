from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import datetime
import os


class Profile(models.Model):
    # Student = 1
    # Employee = 2
    # Other = 3
    # TYPE_CHOICES = (
    #     (Student, 'Student'),
    #     (Employee, 'Asscociate'),
    #     (Other , 'Other'),
    # )
     
    user            = models.OneToOneField(User, on_delete=models.CASCADE)
    image           = models.ImageField(upload_to='profile/%y/%m/%d/', null=True, blank=True)
    organisation    = models.CharField(max_length=50, null=True, blank=True)
    designation     = models.CharField(max_length=50, null=True, blank=True)
    birthdate       = models.DateField(null=True, blank=True)
    city            = models.CharField(max_length=255, null=True, blank=True)
    bio             = models.CharField(max_length=255, null=True, blank=True)
    
    status          = models.BooleanField(default=False)
    updated         = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

        
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


