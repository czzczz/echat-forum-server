###############################
# 用户头像上传接口################
###############################

# 引入外部库
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, HttpResponseServerError,JsonResponse
# from django.shortcuts import render
import filetype, hashlib
import json
import os
import re
import random

from upload.model.user_headers import UserHeaders

from ..settings import header_image_dir, HEADER_BASE_DIR, HEADER_DIR_LENGTH,IMAGE_ALLOWED_EXTENSIONS,HEADER_SIZE_LIMIT

@require_http_methods(['POST'])
def Get(request):
    # 从请求表单中获取文件对象
    file = request.FILES['file']
    if not file:  # 文件对象不存在， 返回400请求错误
        return HttpResponseServerError('001')

    # 计算文件md5
    md5 = _getFileMd5(file)
    uploadfile = UserHeaders.getImageByMd5(md5)
    if uploadfile:   # 文件已存在， 直接返回
        print('文件已有', uploadfile)
        return HttpResponse(json.dumps({'url': uploadfile.getImageUrl()}))

    # 获取扩展类型 并 判断
    ext = _getFileExtension(file)
    isTypeOK, baseDir = _ifTypeAllowed(ext)
    if not isTypeOK:
        return HttpResponseServerError('003 type not allowed')

    # 判断大小    
    if not _ifSizeAllowed(file.size, baseDir):
        return HttpResponseServerError('002 size not allowed')
    # 开始生成随机目录
    addrOneFloor = []
    for depth in range(HEADER_DIR_LENGTH):
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
    uploadfile = UserHeaders()
    uploadfile.img_md5 = md5
    uploadfile.img_type = ext
    uploadfile.img_addr_code = addrCode
    uploadfile.save()  # 插入数据库

    # 保存 文件到磁盘
    try:
        os.makedirs(os.path.join(baseDir, addr))
    except Exception:
        print()

    with open(uploadfile.getImagePath(), "wb") as f:
        # 分块写入
        for chunk in file.chunks():
            f.write(chunk)

    # 返回图片的url以供访问
    return HttpResponse(json.dumps({'url': uploadfile.getImageUrl()}))


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
    if ext in IMAGE_ALLOWED_EXTENSIONS:
        return True, HEADER_BASE_DIR
    else:
        return False, None

# 文件大小限制  
def _ifSizeAllowed(size, baseDir):
    sizeMb = size/(1024 * 1024)
    if baseDir == HEADER_BASE_DIR:
        return True if sizeMb < HEADER_SIZE_LIMIT else False
    else: 
        return False
