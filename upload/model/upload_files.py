from mongoengine import Document, StringField, IntField, DateTimeField
import time
from re import findall
import json

from ..settings import DIR_LENGTH, IMAGE_BASE_DIR, IMAGE_ALLOWED_EXTENSIONS, ARCHIVE_BASE_DIR, ARCHIVE_ALLOWED_EXTENSIONS, ELSE_BASE_DIR, OTHER_ALLOWED_EXTENSIONS

# Create your models here.

class UploadFiles(Document):
    filename = StringField(max_length=256, default="")
    file_md5 = StringField(max_length=128)
    file_type = StringField(max_length=10)
    file_size = IntField()
    file_addr_code = StringField(max_length=(3 * DIR_LENGTH + 1))
    created_at = IntField(default=int(round(time.time() * 1000)))
    updated_at = IntField(default=int(round(time.time() * 1000)))

    
    def _getFileAddrValue(self):
        if len(self.file_addr_code) % 3 != 0:
            return None
        addrList = findall(r'.{3}', self.file_addr_code)
        return '/'.join(addrList) + '/'

    def getFileUrl(self):
        if self.file_type in IMAGE_ALLOWED_EXTENSIONS:
            baseUrl = 'image/'
        elif self.file_type in ARCHIVE_ALLOWED_EXTENSIONS:
            baseUrl = 'archive/'
        else:
            baseUrl = 'else/'
        url =baseUrl + '?file=' + self.file_md5
        return url
    # 获取本图片在本地的位置，即你的文件系统的路径，图片会保存在这个路径下
    def getFilePath(self):
        if self.file_type in IMAGE_ALLOWED_EXTENSIONS:
            basePath = IMAGE_BASE_DIR
        elif self.file_type in ARCHIVE_ALLOWED_EXTENSIONS:
            basePath = ARCHIVE_BASE_DIR
        else:
            basePath = ELSE_BASE_DIR
        path = basePath + self._getFileAddrValue() + self.file_md5 + '.' + self.file_type
        return path
    def __str__(self):
        updateTimeArr = time.localtime(float(self.updated_at / 1000))
        s = {
            'filename': self.filename,
            'fileType': self.file_type,
            'fileSize': self.file_size,
            'fileCode': self.file_addr_code,
            'fileMd5': self.file_md5,
            'lastUpdated': time.strftime('%Y-%m-%d %H:%M:%S', updateTimeArr)
        }
        return json.dumps(s, ensure_ascii=False, indent=4)

    
    @classmethod
    def getFileByMd5(cls, md5):
        try:
            return UploadFiles.objects.filter(file_md5=md5).first()
        except Exception:
            return None
    