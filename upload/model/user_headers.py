from mongoengine import Document, StringField
from re import findall



from ..settings import HEADER_BASE_DIR, header_image_dir, HEADER_DIR_LENGTH


class UserHeaders(Document):
    img_md5 = StringField(max_length=128)
    img_addr_code = StringField(max_length=(3 * HEADER_DIR_LENGTH + 1))
    img_type = StringField(max_length=5)

    def _getImageAddrValue(self):
        if len(self.img_addr_code) % 3 != 0:
            return None
        addrList = findall(r'.{3}', self.img_addr_code)
        return '/'.join(addrList) + '/'

    def getImagePath(self):
        return HEADER_BASE_DIR + self._getImageAddrValue() + self.img_md5 + '.' + self.img_type

    def getImageUrl(self):
        return 'header/?img=' + self.img_md5

    def __str__(self):
        s = self.img_addr_code + '_' + self.img_md5 + '.' + self.img_type
        return s


    @classmethod
    def getImageByMd5(cls, md5):
        try:
            return UserHeaders.objects.filter(img_md5=md5).first()
        except Exception:
            return None