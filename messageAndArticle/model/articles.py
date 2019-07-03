from mongoengine import Document, StringField, ListField, IntField, LongField, DictField
from bson.objectid import ObjectId
import json
import time
import difflib


class Articles(Document):
    _id = StringField(max_length=20)
    title = StringField(max_length=50)
    content = StringField(max_length=10241)
    user = StringField(max_length=25)
    changeHistory = ListField()
    comments = StringField()
    thumbsUp = ListField()
    createdAt = LongField()
    updatedAt = LongField()


    def __str__(self):
        dic = {
            'title': self.title,
            'content': self.content,
            'user': self.user,
            'createdAt': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(self.createdAt / 1000))),
            'updatedAt': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(self.updatedAt / 1000))),
            'changeHistory': self.changeHistory,
        }
        return json.dumps(dic, indent=4)

    @classmethod
    def getArticleById(cls, aid):
        try:
            return Articles.objects(_id=aid).first()
        except Exception as e:
            print(e)
            return None

    @classmethod
    def updateArticle(cls, aid, atc):
        old = Articles.getArticleById(aid)

        changeLog = {
            'title': Articles.getDifferenceList(old.title, atc.title),
            'content': Articles.getDifferenceList(old.content, atc.content),
            'time': int(round(time.time() * 1000)),
        }
        print(changeLog)

        try:
            Articles.objects(_id=aid).update(set__updatedAt=changeLog['time'], set__content=atc['content'], set__title=atc['title'], push__changeHistory=changeLog)
            return changeLog
        except Exception:
            print('更新失败')
            return None

    @classmethod
    def getDifferenceList(cls, s1, s2):
        dic = Articles.getDifferenceDict(s1, s2)
        resultList = []

        for key in dic.keys():
            resultList.append([
                key,
                ''.join(dic[key]['drop']),
                ''.join(dic[key]['add'])
            ])
        return resultList

    @classmethod
    def getDifferenceDict(cls, s1, s2):
        s1_list = list(s1)
        s2_list = list(s2)
        print(s1_list, s2_list)
        #创建对象
        d = difflib.Differ()
        #比较
        diffList = list(d.compare(s1_list, s2_list))

        checkArray = {}
        pin1 = 0
        pin2 = 0
        iscontinue = False

        for s in diffList:
            if s.startswith('-'):
                c = list(s).pop()
                idx = s1_list.index(c, pin1)
                pin1 = idx + 1
                # print('删除', idx, c)
                if not idx in checkArray.keys() and not iscontinue:
                    checkArray[idx] = {
                        'drop': [c],
                        'add': []
                    }
                else:
                    for k in range(idx, -1, -1):
                        if k in checkArray.keys():
                            checkArray[k]['drop'].append(c)
                            break
                iscontinue = True

            elif s.startswith('+'):
                c = list(s).pop()
                idx = s2_list.index(c, pin2)
                pin2 = idx + 1
                # print('添加', idx, c)
                if not idx in checkArray.keys() and not iscontinue:
                    checkArray[idx] = {
                        'drop': [],
                        'add': [c]
                    }
                else:
                    for k in range(idx, -1, -1):
                        if k in checkArray.keys():
                            checkArray[k]['add'].append(c)
                            # print('延长',checkArray[k])
                            break
                iscontinue = True

            else:
                iscontinue = False
                
        return checkArray

