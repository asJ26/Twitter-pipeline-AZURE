from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from scrapper.models import Tweet
from django.views.generic import ListView
import requests
import tweepy
from django.conf import settings
import re
import csv


@login_required
def index(request):
    template = 'dashboard/index.html'
    context = {}
    return render(request, template, context)


class tweets(ListView):
    model = Tweet
    paginate_by = 12
    template_name = "dashboard/tweets.html"


def train(request):
    from scrapper.service import train_model
    template = 'dashboard/train.html'
    context = {
        "title": "Training Result",
        "is_train_result": True,
        "result": train_model(Tweet.objects.filter(is_testing_record=True))
    }
    return render(request, template, context)

def test(request, id=None):
    from scrapper.service import test_model
    template = 'dashboard/train.html'
    try:
        t = Tweet.objects.get(id=id)
    except Tweet.DoesNotExist:
        t = None

    result = test_model(t) if t else "Give the id in input to process"
    context = {
        "title": "Classification Result",
        "is_test_result": True,
        "result": result
    }
    return render(request, template, context)

def import_data(request):
    template = 'dashboard/import.html'
    file = open('static/tweets_formatted_data.csv')
    csv_file = csv.reader(file)
    for row in csv_file:
        is_emergency = True if str(row[0]) == "emergency" else False
        Tweet.objects.create(
            text=row[1],
            username="sample",
            is_emergency=is_emergency,
            is_testing_record=True
        )


@login_required
def fetch_tweets(request):
    template = 'dashboard/fetch_tweets.html'

    api_key = settings.API_KEY
    api_secret = settings.API_SECRET
    bearer_token = settings.BEARER_TOKEN
    access_token = settings.ACCESS_TOKEN
    aacess_secret = settings.ACCESS_SECRET

    auth = tweepy.OAuthHandler(api_key, api_secret)
    auth.set_access_token(access_token, aacess_secret)
    api = tweepy.API(auth)

    result = api.search_tweets(q='#indianrailway', lang='en', count=20)
    for item in result:
        try:
            t = Tweet.objects.get(tid=item.id_str)
        except Tweet.DoesNotExist:
            t = Tweet.objects.create(tid=item.id_str)

        t.tid=item.id_str
        t.tweet = item.text
        t.text= item.text
        t.username= item.user.name
        t.user= request.user
        t.timestamp= item.created_at
        t.likes= item.favorite_count
        t.save()

    context = {
        "result": result
    }
    return render(request, template, context)



def check_sentiment(request, id=None):
    from scrapper.service import get_sentiment
    template = 'dashboard/train.html'
    result = None
    if id:
        result = Tweet.objects.get(id=id)
        result.score = get_sentiment(result.text)
        if result.score < 0:
            result.is_negative = True
        result.save()

    context = {
        "title": "Sentiment Result",
        "is_sentiment_result": True,
        "result": result,
        "item": result
    }
    return render(request, template, context)