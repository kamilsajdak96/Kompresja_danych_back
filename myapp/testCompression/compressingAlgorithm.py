import zlib

def test():
    with open("imageTest.png", "rb") as in_file:
        compressed = zlib.compress(in_file.read(), 9)
    with open("MyCompressedFile", "wb") as out_file:
        out_file.write(compressed)