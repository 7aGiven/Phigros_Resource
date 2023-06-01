import shutil
import os
from zipfile import ZipFile
import sys
import json
import base64
from concurrent.futures import ThreadPoolExecutor
from UnityPy import Environment
from UnityPy.enums import ClassIDType
from io import BytesIO


for directory in ("music", "avatar", "illustrationLowRes"):
    shutil.rmtree(directory, True)
    os.mkdir(directory)


env = Environment()
with ZipFile(sys.argv[1]) as apk:
    for name in apk.namelist():
        if name.startswith("assets/aa/Android/"):
            with apk.open(name) as f:
                env.load_file(f.read(), name = name[-39:])
    with apk.open("assets/aa/catalog.json") as f:
        data = json.load(f)


key = base64.b64decode(data["m_KeyDataString"])
bucket = base64.b64decode(data["m_BucketDataString"])
entry = base64.b64decode(data["m_EntryDataString"])



class ByteReader:
    def __init__(self, data):
        self.data = data
        self.position = 0

    def readInt(self):
        self.position += 4
        return self.data[self.position-4]^self.data[self.position-3]<<8^self.data[self.position-2]<<16

table = []
reader = ByteReader(bucket)
for x in range(reader.readInt()):
    print(x, end=" ")
    key_position = reader.readInt()
    key_type = key[key_position]
    key_position += 1
    if key_type == 0:
        length = key[key_position]
        key_position += 4
        key_value = key[key_position:key_position+length].decode()
    elif key_type == 1:
        length = key[key_position]
        key_position += 4
        key_value = key[key_position:key_position+length].decode("utf16")
    elif key_type == 4:
        key_value = key[key_position]
    else:
        raise BaseException(key_position, key_type)
    print(key_value, end=" ")
    for i in range(reader.readInt()):
        entry_position = reader.readInt()
        entry_value = entry[4+28*entry_position:4+28*entry_position+28]
        entry_value = entry_value[8]^entry_value[9]<<8
    print(entry_value)
    table.append((key_value, entry_value))


def io(path, resource):
    if type(resource) == BytesIO:
        with open(path, "wb") as f:
            f.write(resource.getbuffer())
        resource.close()
    else:
        with open(path, "wb") as f:
            f.write(resource)


"""
save里是各种文件的写入，不需要的可以注释掉。
"""
classes = ClassIDType.TextAsset, ClassIDType.Sprite, ClassIDType.AudioClip
def save(key, entry):
    print(key, entry)
    if key[-12:] == ".0/music.wav":
        key = key[:-12]
        obj = env.files[entry].get_filtered_objects(classes)
        obj = next(obj).read()
        ioPool.submit(io, "music/%s.wav" % key, obj.samples["music.wav"])
    elif key[-25:] == ".0/IllustrationLowRes.png":
        key = key[:-25]
        obj = env.files[entry].get_filtered_objects(classes)
        obj = next(obj).read()
        bytesIO = BytesIO()
        obj.image.save(bytesIO, "png")
        ioPool.submit(io, "illustrationLowRes/%s.png" % key, bytesIO)
    elif key[:7] == "avatar.":
        key = key[7:]
        obj = env.files[entry].get_filtered_objects(classes)
        obj = next(obj).read()
        bytesIO = BytesIO()
        obj.image.save(bytesIO, "png")
        ioPool.submit(io, "avatar/%s.png" % key, bytesIO)


with ThreadPoolExecutor(1) as ioPool:
    with ThreadPoolExecutor(min(8, os.cpu_count())) as pool:
        for key, entry in table:
            if type(key) == int:
                continue
            if key[:7] == "avatar.":
                pool.submit(save, key, table[entry][0])
            elif key[:14] == "Assets/Tracks/" and key[14] != "#":
                pool.submit(save, key[14:], table[entry][0])