# 引入外部库
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, HttpResponseServerError, JsonResponse
# from django.shortcuts import render
import filetype, hashlib
import json
import os
import re
import random
# 引入模块
from ..model.upload_files import UploadFiles
# 引入配置
from ..settings import IMAGE_BASE_DIR, IMAGE_SIZE_LIMIT, IMAGE_ALLOWED_EXTENSIONS, DIR_LENGTH

# Create your views here.

@require_http_methods(["POST"])
def Get(request):
    # 从请求表单中获取文件对象
    file = request.FILES['file']
    if not file:  # 文件对象不存在， 返回400请求错误
        return HttpResponseServerError('001')

    # 图片大小限制
    if not _ifSizeAllowed(file.size):
        return HttpResponseServerError('002')

    # 计算文件md5
    md5 = _getFileMd5(file)
    uploadImg = UploadFiles.getFileByMd5(md5)
    if uploadImg:   # 图片文件已存在， 直接返回
        print('文件已有', uploadImg)
        return JsonResponse({'url': uploadImg.getImageViewer()})

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

    # 检测通过 创建新的image对象
    # 文件对象即上一小节的UploadImage模型
    uploadImg = UploadFiles()
    uploadImg.filename = _getSecureFileName(file.name)
    uploadImg.file_size = file.size
    uploadImg.file_md5 = md5
    uploadImg.file_type = ext
    uploadImg.file_addr_code = addrCode
    uploadImg.save()  # 插入数据库
    # print(uploadImg)

    # 保存 文件到磁盘
    try:
        os.makedirs(os.path.join(IMAGE_BASE_DIR, addr))
    except Exception:
        print()

    with open(uploadImg.getFilePath(), "wb") as f:
        # 分块写入
        for chunk in file.chunks():
            f.write(chunk)

    # 返回图片的url以供访问
    return JsonResponse({'url': uploadImg.getImageViewer()})




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
    return True if ext in IMAGE_ALLOWED_EXTENSIONS else False

# 文件大小限制  
def _ifSizeAllowed(size):
    sizeMb = size/(1024 * 1024)
    return True if sizeMb < IMAGE_SIZE_LIMIT else False
