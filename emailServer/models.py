from mongoengine import Document, DateTimeField, DictField
import json
import time

# Create your models here.

class Users(Document):
    createdAt = DateTimeField()
    services = DictField()
    emails = DictField()
    profile = DictField()



    @classmethod
    def getUserByEmail(cls, email):
        try:
            return Users.objects(profile__email=email).first()
        except Exception:
            return None

    @classmethod
    def verifyEmails(cls, emails):
        newEmails = []
        for email in emails:
            email['verified'] = True
            newEmails.append(email)
        print('new Emails', newEmails)
        log = {
            'operation': 'verify',
            'operator': 'admin',
            'time': int(round(time.time() * 1000)),
            'detail': 'verify email ' + newEmails[0]['address']
        }
        try:
            Users.objects(profile__email=newEmails[0]['address']).update(set__emails=newEmails, push__profile__history=log, set__profile__status=1)
            return True
        except Exception:
            return False