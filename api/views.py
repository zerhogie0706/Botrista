from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.


def login(request):
    print('AAA')
    return JsonResponse({"msg": "success"})
