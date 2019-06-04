from django.urls import path

from messageAndArticle.view.messages import Update

urlpatterns = [
    path('update', Update),
]