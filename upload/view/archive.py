# 引入外部库
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, HttpResponseServerError
# from django.shortcuts import render
import filetype, hashlib
import json
import os
import re
import random

from upload.model.upload_files import UploadFiles

from ..settings import archive_dir, ARCHIVE_ALLOWED_EXTENSIONS, ARCHIVE_BASE_DIR, ARCHIVE_SIZE_LIMIT, DIR_LENGTH

@require_http_methods(['POST'])
def Get(request):
    # 从请求表单中获取文件对象
    file = request.FILES['file']
    if not file:  # 文件对象不存在， 返回400请求错误
        return HttpResponseServerError('001')

    if not _ifSizeAllowed(file.size):
        return HttpResponseServerError('002 size not allowed')

    # 计算文件md5
    md5 = _getFileMd5(file)
    uploadfile = UploadFiles.getFileByMd5(md5)
    if uploadfile:   # 文件已存在， 直接返回
        print('文件已有', uploadfile)
        return HttpResponse(json.dumps({'url': uploadfile.getFileUrl()}))

    # 获取扩展类型 并 判断
    ext = _getFileExtension(file)
    if not _ifTypeAllowed(ext):
        return HttpResponseServerError('003')

    # 开始生成随机目录
    addrOneFloor = []
    for depth in range(DIR_LENGTH):
        str = ''
        for len in range(3):
            # 生成3位随机数字拼成字符串
            ch = chr(random.randrange(ord('0'), ord('9') + 1))
            str += ch
        addrOneFloor.append(str)
    addr = '/'.join(addrOneFloor) + '/'
    addrCode = ''.join(addrOneFloor)

    # 检测通过 创建新的对象
    # 文件对象即上一小节的模型
    uploadfile = UploadFiles()
    uploadfile.filename = _getSecureFileName(file.name)
    uploadfile.file_size = file.size
    uploadfile.file_md5 = md5
    uploadfile.file_type = ext
    uploadfile.file_addr_code = addrCode
    uploadfile.save()  # 插入数据库

    # 保存 文件到磁盘
    try:
        os.makedirs(os.path.join(ARCHIVE_BASE_DIR, addr))
    except Exception:
        print()

    with open(uploadfile.getFilePath(), "wb") as f:
        # 分块写入
        for chunk in file.chunks():
            f.write(chunk)

    # 返回图片的url以供访问
    return HttpResponse(json.dumps({'url': uploadfile.getFileUrl()}))




def _getSecureFileName(name):
    return '_'.join(re.split(r'[^(\w|\.)]+', name))

def _getFileExtension(file):
    fileData = bytearray()
    for c in file.chunks():
        fileData += c
    try:
        ext = filetype.guess_extension(fileData)
        return ext
    except Exception:
        # todo log
        return None

# 计算md5
def _getFileMd5(file):
    obj = hashlib.md5()
    for chunk in file.chunks():
        obj.update(chunk)
    return obj.hexdigest()

# 文件类型过滤
def _ifTypeAllowed(ext):
    return True if ext in ARCHIVE_ALLOWED_EXTENSIONS else False

# 文件大小限制  
def _ifSizeAllowed(size):
    sizeMb = size/(1024 * 1024)
    return True if sizeMb < ARCHIVE_SIZE_LIMIT else False
