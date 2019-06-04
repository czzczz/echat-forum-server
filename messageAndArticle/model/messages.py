from mongoengine import Document, StringField, ListField, IntField, DictField
from bson.objectid import ObjectId
import json
import time
import difflib



class Messages(Document):
    _id = StringField(max_length=20)
    content = StringField(max_length=151)
    user = StringField(max_length=25)
    tags = ListField()
    changeHistory = ListField()
    comments = ListField()
    thumbsUp = ListField()
    createdAt = IntField()
    updatedAt = IntField()


    def getContentDifferenceList(self, s2):
        dic = self.getContentDifferenceDict(s2)
        resultList = []

        for key in dic.keys():
            resultList.append([
                key,
                ''.join(dic[key]['drop']),
                ''.join(dic[key]['add'])
            ])
        return resultList

    def getContentDifferenceDict(self, s2):
        s1_list = list(self.content)
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
                
        print('asdfasdfasdfasdfasdfasdf',checkArray)
        return checkArray


    def getTagsDifferenceDict(self, l2):
        tagValueList1 = []
        tagValueList2 = []
        for tag in self.tags:
            tagValueList1.append(tag['value'])
        for tag in l2:
            tagValueList2.append(tag['value'])
        d = difflib.Differ()
        diff = d.compare(tagValueList1, tagValueList2)
        # print(list(diff))

        dropValueList = []
        addValueList = []    
        for s in list(diff):
            if s.startswith('-'):
                # print(s)
                content = s.split().pop()
                dropValueList.append(content)
            elif s.startswith('+'):
                # print(s)
                content = s.split().pop()
                addValueList.append(content)

        dropTagList = []
        addTagList = []
        for tag in self.tags:
            if tag['value'] in dropValueList:
                dropTagList.append(tag)

        for tag in l2:
            if tag['value'] in addValueList:
                addTagList.append(tag)
        changeObj = {
            'drop': dropTagList,
            'add': addTagList
        }
        # print(changeObj)
        return changeObj

    def __str__(self):
        dic = {
            'content': self.content,
            'user': self.user,
            'tags': self.tags,
            'createdAt': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(self.createdAt / 1000))),
            'updatedAt': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(self.updatedAt / 1000))),
            'changeHistory': self.changeHistory,
        }
        return json.dumps(dic, indent=4)

    @classmethod
    def getCleanedCharListFromString(cls, s):
        l = list(s)
        for k, c in enumerate(l):
            if c.isspace():
                l[k] = '?+'
        return l

    @classmethod
    def getMessageById(cls, mid):
        # print(mid)
        try:
            return Messages.objects(_id=mid).first()
        except Exception as e:
            print(e)
            return None

    @classmethod
    def updateMessage(cls, mid, msg):
        old = Messages.getMessageById(mid)
        # print(old)
        changeLog = {
            'content': old.getContentDifferenceList(msg['content']),
            'tags': old.getTagsDifferenceDict(msg['tags']),
            'time': int(round(time.time() * 1000)),
        }
        print(changeLog)
        # s1 = old['content']
        # s2 = msg['content']
        # print('原本字符串', s1)
        # print('新字符串', s2)
        # for chg in changeLog['content']:
        #     s1 = s1[:chg[0]] + chg[2] + s1[len(chg[1]) + chg[0]:]
        # for i in range(len(changeLog['content']), 0, -1):
        #     chg = changeLog['content'][i - 1]
        #     s2 = s2[:chg[0]] + chg[1] + s2[len(chg[2]) + chg[0]:]
        # print('源字符串改变', s1)
        # print('新字符串回滚', s2)
        try:
            Messages.objects(_id=mid).update(set__updatedAt=changeLog['time'], set__content=msg['content'], set__tags=msg['tags'], push__changeHistory=changeLog)
            return changeLog
        except Exception:
            print('更新失败')
            return None
