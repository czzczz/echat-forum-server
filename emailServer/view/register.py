from django.shortcuts import render
import json
import time
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail

from ..models import Users

from django.conf import settings
from ..settings import DOMAIN_DICT, MAIL_HOME_DICT, NAME_ENCODE_DICT, HOST_ADDR_BASE

# Create your views here.

@require_http_methods(["POST"])
def sendCheck(request):
    userInfo = json.loads(request.body)['userInfo']
    # print(userInfo)

    # 生成校验地址的url参数
    urlArg, timeS = _encodeUrlArg(userInfo['email'])

    url = HOST_ADDR_BASE + 'email/register/comfirm/?check=' + urlArg
    print(url)

    # 发送邮件
    email_title = '确认你的论坛账户邮箱'
    email_body = 'please click ' + url
    email = userInfo['email'] 
    send_status = send_mail(email_title, email_body, settings.EMAIL_FROM, [email])

    if send_status:
        # 发送成功
        print('email sent')
        return JsonResponse({'status': 'OK', 'time': timeS})
    else:
        return JsonResponse({'status': 'ERR'})
    

@require_http_methods(["GET"])
def comfirmAndLogin(request):
    # 获取参数
    arg = request.GET['check']

    # 参数翻译，获取参数中的用户信息与时间戳
    userEmail, timeS = _decodeUrlArg(arg)
    
    # 根据参数中的用户信息查找数据库中的用户
    user = Users.getUserByEmail(userEmail)

    if not user:
        print('No such user')
        return render(request, 'registerUrlTimeOut.html')

    # 检查验证邮件的发送时间与验证链接被点击的时间是否在一定时间内
    if _checkTime(user, timeS):
        print('OK, user email verifying')
        # 邮箱验证
        Users.verifyEmails(user['emails'])
        return render(request, 'registerComfirmOK.html')
    else:
        print('time not OK')
        return render(request, 'registerUrlTimeOut.html')



def _encodeUrlArg(userEmail):
    urlArg = ''
    host = userEmail.split('@')
    name = host.pop(0)

    # 邮箱名转译
    encodeName = ''
    for char in name:
        encodeName += NAME_ENCODE_DICT[char]

    # 域名转译
    domainList = host[0].split('.')
    homeCode = MAIL_HOME_DICT[domainList.pop(0)]
    domainCode = ''
    for doamin in domainList:
        domainCode += DOMAIN_DICT[doamin]

    # 获取当前时间戳
    timeS = int(round(time.time() * 1000))

    timeStr = hex(timeS)
    timeStrCode = ''
    for char in timeStr:
        timeStrCode += NAME_ENCODE_DICT[char]

    urlArg = timeStrCode + '-' +  encodeName + "_" + domainCode + homeCode
    return urlArg, timeS


def _decodeUrlArg(arg):
    # 转译字典翻转，用以反转译
    name_decode_dict = {}
    domain_decode_dict = {}
    home_decode_dict = {}

    for key, value in NAME_ENCODE_DICT.items():
        name_decode_dict[value] = key

    for key, value in DOMAIN_DICT.items():
        domain_decode_dict[value] = key

    for key, value in MAIL_HOME_DICT.items():
        home_decode_dict[value] = key

    # 获取时间戳
    userCheck = arg.split('-')
    timeCode = userCheck.pop(0)
    timeStr = ''
    for char in timeCode:
        timeStr += name_decode_dict[char]
    time = int(timeStr, 16)

    # 获取邮箱名
    userCheck = userCheck[0].split('_')
    nameCode = userCheck.pop(0)
    name = ''
    for char in nameCode:
        name += name_decode_dict[char]

    # 获取邮箱后缀
    domainCodeList = list(userCheck[0])
    home = home_decode_dict[domainCodeList.pop()]
    domain = []
    for char in domainCodeList:
        domain.append(domain_decode_dict[char])
    domain = '.'.join([home, '.'.join(domain)])

    return '@'.join([name, domain]), time


def _checkTime(user, timeS):
    logs = user['profile']['history']
    # if len(logs) > 1:
    #     print('user not new')
    #     return False
    log0 = logs[0]
    registerTime = int(log0['time'])
    nowTime = int(round(time.time() * 1000))
    if registerTime == timeS and nowTime - registerTime < 1800000:
        return True
    return False




