import os
from django.conf import settings


#存入的图片将随机生成 DIR_LENGTH 数量的3位随机字符串（纯数字）作为文件夹名称，目的是防止单文件夹内文件过多
#默认数量为2,
#若第一个字符串为‘123’，第二个字符串为‘321’
#那么上传的图片问价将被置于目录
#       ${***BASE_DIR}/123/321/
DIR_LENGTH = 2 

archive_dir = 'archive/'
ARCHIVE_BASE_DIR = os.path.join(settings.RESOURCES_DIR, archive_dir)
ARCHIVE_SIZE_LIMIT = 2048
ARCHIVE_ALLOWED_EXTENSIONS = set(['zip', 'rar', 'tar', '7z', 'bz2', 'gz', 'xz'])


image_dir = 'image/' 
IMAGE_BASE_DIR = os.path.join(settings.RESOURCES_DIR, image_dir) # 图片上传存储的位置
IMAGE_SIZE_LIMIT = 10 #Mb 图片上传文件大小限制
IMAGE_ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg']) # 图片上传类型限制


HEADER_DIR_LENGTH = 2
header_image_dir = 'header/' # 用户头像
HEADER_BASE_DIR = os.path.join(settings.RESOURCES_DIR, header_image_dir)
HEADER_SIZE_LIMIT = 2 # Mb


else_dir = 'else/'
ELSE_BASE_DIR = os.path.join(settings.RESOURCES_DIR, else_dir)


OTHER_ALLOWED_EXTENSIONS = set(['pdf'])
OTHER_SIZE_LIMIT = 50