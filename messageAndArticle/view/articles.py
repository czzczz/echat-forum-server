from django.views.decorators.http import require_http_methods
from django.http import JsonResponse,HttpResponse
import json

from messageAndArticle.model.articles import Articles


@require_http_methods(['POST'])
def Update(request):
    para = json.loads(request.body)
    aid = para['articleId']
    atc = para['article']

    clog = Articles.updateArticle(aid, atc)

    return JsonResponse({'code': 200, 'changeLog': clog})

