from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.http import require_http_methods
import os

from django.conf import settings

from upload.model.upload_files import UploadFiles


@require_http_methods(["GET"])
def serve(request):
    md5 = request.GET['file']
    userCheck = request.GET['user']

    if not userCheck:
        return HttpResponseNotFound('No such file')

    file = UploadFiles.getFileByMd5(md5)
    if not file:
        return HttpResponseNotFound('no file')
    print('get file', file)

    fullPath = file.getFilePath()

    if not os.access(fullPath, os.R_OK):
        return HttpResponseNotFound('File Not Found')

    response = HttpResponse(_getFileContent(fullPath, 5), content_type='APPLICATION/OCTET-STREAM') 
    response['Content-Disposition'] = 'attachment; filename='+file.filename
    response['Content-Length'] = file.file_size
    return response




def _getFileContent(filePath, bufSize):
    with open(filePath, 'rb') as f:
        while True:#循环读取
            c = f.read(bufSize*1024*1024)
            if c:
                yield c
            else:
                break
