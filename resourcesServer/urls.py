from django.urls import path

from resourcesServer.view import image
from resourcesServer.view import download
from resourcesServer.view import header

urlpatterns = [
    path('image/', image.serve),
    path('download/', download.serve),
    path('header/', header.serve),
]