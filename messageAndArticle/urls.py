from django.urls import path

from messageAndArticle.view.messages import Update as MessageUpdate
from messageAndArticle.view.articles import Update as ArticleUpdate

urlpatterns = [
    path('message', MessageUpdate),
    path('article', ArticleUpdate),
]