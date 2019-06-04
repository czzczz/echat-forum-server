from django.urls import path

import emailServer.view.register as emailRegister

urlpatterns = [
    path("register/to", emailRegister.sendCheck),
    path("register/comfirm/", emailRegister.comfirmAndLogin)
]