from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import json
from . import imageTester
from myapp.models import Image

def index(request):
    response = json.dumps([{}])
    return HttpResponse(response, content_type='text/json')

def getImage(request, image_name):
    if request.method == 'GET':
        try:
            image = Image.objects.get(name=image_name)
            response = json.dumps([{ 'Image': image.name}])
        except:
            response = json.dumps([{ 'Error': 'No such image'}])
    return HttpResponse(response, content_type='text/json')

@csrf_exempt
def addImage(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        image_name = payload['image_name']
        print(image_name[22:])
        imageTester.test(image_name[22:])
        image = Image(name=image_name)
        try:
            image.save()
            response = json.dumps([{ 'Success': 'Image added successfully!'}])
        except:
            response = json.dumps([{ 'Error': 'Image could not be added!'}])
    return HttpResponse(response, content_type='text/json')