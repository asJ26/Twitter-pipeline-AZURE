from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='user'),
    path('tweets/', views.tweets.as_view(), name='tweets'),
    path('fetch_tweets/', views.fetch_tweets, name='fetch_tweets'),
    path('check_s/<slug:id>/', views.check_sentiment, name='check_sentiment'),
    path('train/', views.train, name='train'),
    path('test/', views.test, name='test'),
    path('test/<slug:id>/', views.test, name='test'),
    path('import_data/', views.import_data, name='import_data')
]
