
from django.urls import path

import upload.view.image as uploadImage
import upload.view.archive as uploadArchive

urlpatterns = [
    path('image', uploadImage.Get),
    path('archive', uploadArchive.Get),
]