import random
import json

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from .utils import top_addresses

@csrf_exempt
def parse(request):
    address = str.strip(request.POST.get('address', ''))
    city = str.strip(request.POST.get('city', ''))
    top = top_addresses(address, city)
    if top:
        return HttpResponse(json.dumps({'status': 0, 'data': {'address': top[0]}}))
    return HttpResponse(json.dumps({'status': 1, 'data':{}}))

@csrf_exempt
def parse5(request):
    address = str.strip(request.POST.get('address', ''))
    city = str.strip(request.POST.get('city', ''))
    top = top_addresses(address, city)
    if top:
        return HttpResponse(json.dumps({'status': 0, 'data': {'address': top[:5]}}))
    return HttpResponse(json.dumps({'status': 1, 'data':{}}))