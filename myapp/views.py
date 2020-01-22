import json
import time
import simplejson as sjson
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from myapp.adaptive_huffman import main
from myapp.models import Image
from myapp.testCompression import compression
from . import imageTester


def index(request):
    response = json.dumps([{}])
    return HttpResponse(response, content_type='text/json')


@csrf_exempt
def addImage(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        image_name = payload['image_name']
        print(image_name[22:])
        text_file = open("Output.txt", "w")
        text_file.write(image_name)
        text_file.close()
        imageTester.test(image_name[22:])
        image = Image(name=image_name)
        try:
            image.save()
            response = json.dumps([{'Success': 'Image added successfully!'}])
        except:
            response = json.dumps([{'Error': 'Image could not be added!'}])
    return HttpResponse(response, content_type='text/json')


def getAllImages(request):
    if request.method == 'GET':
        compression.main('C:/Users/Kamil/Desktop/Kompresja/Kompresja/imageTest.png')
        time.sleep(3)
        lusakujaTxt = open("C:/Users/Kamil/Desktop/Kompresja/Kompresja/Lusakuja.txt", "r")
        lusakuja = lusakujaTxt.read()
        print(lusakuja)
        # main.run('C:/Users/Kamil/Desktop/Kompresja/Kompresja/imageTest.png')
        huffmanTxt = open("C:/Users/Kamil/Desktop/Kompresja/Kompresja/Huffman.txt", "r")
        huffman = huffmanTxt.read()
        print(huffman)
        response = sjson.dumps([{'image_name': "data:image/jpeg;base64," + lusakuja,
                                 'compression_time': compression.times()[0],
                                 'decompression_time': compression.times()[1]
                                 },
                                {'image_name': "data:image/jpeg;base64," + huffman,
                                 'compression_time': main.times()[0],
                                 'decompression_time': main.times()[1],
                                 }])
                                # {'image_name': "data:image/jpeg;base64," + 'asdas',
                                #  'compression_time': "main.times()[0]",
                                #  'decompression_time': "main.times()[1]",
                                #  }])
        print(response)
        
    
    return HttpResponse(response, content_type='text/json')

def getImage(request, image_name):
    response = json.dumps([{}])
    return HttpResponse(response, content_type='text/json')
