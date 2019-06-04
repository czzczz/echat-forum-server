from django.views.decorators.http import require_http_methods
from django.http import JsonResponse,HttpResponse
from mongoengine.queryset.visitor import Q
import json
import time
import difflib


from ..model.messages import Messages


@require_http_methods(['POST'])
def Update(request):
    para = json.loads(request.body)
    mid = para['id']
    msg = para['newMessage']
    # print(mid)
    # print(msg)

    # res = Messages.objects.filter(_id=mid).first()
    # # print(res)
    # # print('old', res)
    # # print('new', msg)
    # # print('content change', getStringDifferenceList(res['content'], msg['content']))
    # # print('tag change', getTagsDifferenceDict(res['tags'], msg['tags']))
    # timeS = int(round(time.time() * 1000))
    # changeLog = {
    #     'contentChange': getStringDifferenceList(res['content'], msg['content']),
    #     'tagChange': getTagsDifferenceDict(res['tags'], msg['tags']),
    #     'time': timeS,
    # }
    # print('change', changeLog)
    # Messages.updateMessage(mid, msg['content'], changeLog)
    Messages.updateMessage(mid, msg)
    # print(Messages.getMessageById(mid).getContentDifferenceList(msg['content']))
    return HttpResponse("OK")


def getStringDifferenceList(s1, s2):
    dic = getStringDifferenceDict(s1, s2)
    resultList = []

    for key in dic.keys():
        resultList.append([
            key,
            ''.join(dic[key]['drop']),
            ''.join(dic[key]['add'])
        ])
    return resultList

def getStringDifferenceDict(s1, s2):
    s1_list = list(s1)
    s2_list = list(s2)
    #创建对象
    d = difflib.Differ()
    #比较
    diff = d.compare(s1_list, s2_list)

    checkArray = {}
    checkId1 = 0
    sContinue = False
    checkId2 = 0
    for s in list(diff):
        if s.startswith('-'):
            # print(s)
            content = s.split().pop()
            originIndex = s1_list.index(content, checkId1)
            if not originIndex in checkArray.keys():
                checkArray[originIndex] = {
                    'drop': [],
                    'add': []
                }
                sContinue = True
            checkArray[originIndex]['drop'].append(content)
            if not sContinue:
                checkId1 = originIndex + 1


        elif s.startswith('+'):
            # print(s)
            content = s.split().pop()
            originIndex = s2_list.index(content, checkId2)
            if not originIndex in checkArray.keys():
                checkArray[originIndex] = {
                    'drop': [],
                    'add': []
                }
                sContinue = True
            checkArray[originIndex]['add'].append(content)
            if not sContinue:
                checkId2 = originIndex + 1

        # elif s.startswith('?'):
        #     isContinue = True

        else:
            sContinue = False

    resultObj = {}
    keyList = list(checkArray.keys())
    keyBuf = keyList.pop(0)
    keyNow = keyBuf
    resultObj[keyNow] = checkArray[keyBuf]
    for key in keyList:
        if key == keyBuf + 1:
            resultObj[keyNow]['drop'].extend(checkArray[key]['drop'])
            resultObj[keyNow]['add'].extend(checkArray[key]['add'])
            keyBuf = key
        else:
            resultObj[key] = checkArray[key]
            keyBuf = key
            keyNow = key
    return resultObj


def getTagsDifferenceDict(l1, l2):
    tagValueList1 = []
    tagValueList2 = []
    for tag in l1:
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
    for tag in l1:
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