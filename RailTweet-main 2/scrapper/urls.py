from django.urls import path
from . import views

urlpatterns = [
    path('iceland/', views.iceland, name='iceland'),
]
