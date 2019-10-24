import base64

def test(base):
    with open("imageTest.png", "wb") as fh:
        fh.write(base64.decodebytes(base.encode()))