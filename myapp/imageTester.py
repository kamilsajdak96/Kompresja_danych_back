import base64

def test(base):
    with open("imageTest.png", "wb") as fh:
        fh.write(base64.decodebytes(base.encode()))


def saveImage(path, file):
    # text_file = open("C:/Users/Kamil/Desktop/Kompresja/Kompresja/Output.txt", "r")
    # img = text_file.read()
    with open(path, "rb") as image_file:
        data = base64.b64encode(image_file.read()).decode('ascii')
    text_file = open(file, "w")
    text_file.write(data)
    text_file.close()
    # print(img[22:])
    print(data)
    return data