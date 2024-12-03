from django.contrib import admin
from . import models
# Register your models here.



class TweetAdmin(admin.ModelAdmin):
    model = models.Tweet
    list_display = ('id', 'score', 'text', 'is_negative', 'is_reviewd', 'is_emergency', 'created')
    list_editable = ('is_negative', 'is_reviewd', 'is_emergency')

admin.site.register(models.Tweet, TweetAdmin)