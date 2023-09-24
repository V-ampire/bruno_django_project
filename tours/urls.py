from django.urls import path

from tours.views import get_all_tours


urlpatterns = [
    path('', get_all_tours, name='index'),
]
