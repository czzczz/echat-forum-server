from django.urls import path

from resourcesServer.view import image
from resourcesServer.view import download

urlpatterns = [
    path('image/', image.serve),
    path('download/', download.serve)
]