from django.db import transaction
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from ..models import RecRival, Rival
from ..serializers.boj import RecRivalSerializers,RivalSerializers
from rest_framework.response import Response
import pandas as pd

@api_view(['POST'])
def verify(request):
    df = pd.read_csv("./users.csv")
    found = request.data["boj"] in df['handle'].unique()
    if found:
        return JsonResponse({"result":"complete","message":"존재하는 백준아이디입니다."})
    return JsonResponse({"result": "error", "message": "존재하지 않는 백준아이디입니다."})


@api_view(['GET'])
def list_rec_rival(request):
    rec_rivals = RecRival.objects.filter(follower=request.user)
    serializers = RecRivalSerializers(rec_rivals, many=True)

    return Response(serializers.data)

@api_view(['POST'])
def handle_rival(request):
    follower = request.user

    if Rival.objects.filter(follower=follower,name=request.data["name"]).exists():
        with transaction.atomic():
            rival = Rival.objects.get(follower=follower,name=request.data["name"])
            rival.delete()
            if not RecRival.objects.filter(follower=follower,name=request.data["name"]).exists():
                rec_rival_serializers = RecRivalSerializers(data=request.data)
                rec_rival_serializers.is_valid(raise_exception=True)
                rec_rival_serializers.save(follower=follower)
    else:
        with transaction.atomic():
            if RecRival.objects.filter(follower=follower,name=request.data["name"]).exists():
                rec_rival = RecRival.objects.get(follower=follower, name=request.data["name"])
                rec_rival.delete()
            rival_serializers = RivalSerializers(data=request.data)
            rival_serializers.is_valid(raise_exception=True)
            rival_serializers.save(follower=follower)

    return Response(rival_serializers.data)
