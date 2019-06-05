from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.http import require_http_methods
import os

from django.conf import settings

from upload.model.user_headers import UserHeaders


@require_http_methods(["GET"])
def serve(request):
    md5 = request.GET['img']

    img = UserHeaders.getImageByMd5(md5)
    if not img:
        return HttpResponseNotFound('No such file')
    # print('get img', img)

    fullPath = img.getImagePath()

    if not os.access(fullPath, os.R_OK):
        return HttpResponseNotFound('Image Not Found')

    response = HttpResponse(_getFileContent(fullPath, 5), content_type='image/' + img.img_type)
    # response = HttpResponse(_getFileContent(fullPath, 5), content_type='APPLICATION/OCTET-STREAM') 
    # response['Content-Disposition'] = 'attachment; filename='+img.filename
    # response['Content-Length'] = img.file_size
    return response




def _getFileContent(filePath, bufSize):
    with open(filePath, 'rb') as f:
        while True:# 循环读取
            c = f.read(bufSize*1024*1024)
            if c:
                yield c
            else:
                break
