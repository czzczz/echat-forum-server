
from django.urls import path

import upload.view.image as uploadImage
import upload.view.archive as uploadArchive
import upload.view.header as uploadHeader

urlpatterns = [
    path('image', uploadImage.Get),
    path('archive', uploadArchive.Get),
    path('header', uploadHeader.Get),
]