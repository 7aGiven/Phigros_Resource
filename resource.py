import base64
from configparser import ConfigParser
import json
import os
import shutil
import sys
from zipfile import ZipFile



os.chdir(__file__[:-11])

config = ConfigParser()
config.read("config.ini")
types = config["TYPES"]
type_turple = ("avatar", "Chart_EZ", "Chart_HD", "Chart_IN", "Chart_AT", "illustrationBlur", "illustrationLowRes", "illustration", "music")




with ZipFile(sys.argv[1]) as apk:
    with apk.open("assets/aa/catalog.json") as f:
        data = json.load(f)


for directory in filter(lambda x:types.getboolean(x), type_turple):
    shutil.rmtree(directory, True)
    os.mkdir(directory)


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


def save_compress(key, entry):
    if types.getboolean("avatar") and key[:7] == "avatar.":
        key = key[7:]
        with apk.open("assets/aa/Android/%s" % entry) as bundle:
            with open("avatar/%s.bundle" % key, "wb") as f:
                f.write(bundle.read())
    elif types.getboolean("Chart_EZ") and key[-14:] == "/Chart_EZ.json":
        key = key[:-14]
        with apk.open("assets/aa/Android/%s" % entry) as bundle:
            with open("Chart_EZ/%s.bundle" % key, "wb") as f:
                f.write(bundle.read())
    elif types.getboolean("Chart_HD") and key[-14:] == "/Chart_HD.json":
        key = key[:-14]
        with apk.open("assets/aa/Android/%s" % entry) as bundle:
            with open("Chart_HD/%s.bundle" % key, "wb") as f:
                f.write(bundle.read())
    elif types.getboolean("Chart_IN") and key[-14:] == "/Chart_IN.json":
        key = key[:-14]
        with apk.open("assets/aa/Android/%s" % entry) as bundle:
            with open("Chart_IN/%s.bundle" % key, "wb") as f:
                f.write(bundle.read())
    elif types.getboolean("Chart_AT") and key[-14:] == "/Chart_AT.json":
        key = key[:-14]
        with apk.open("assets/aa/Android/%s" % entry) as bundle:
            with open("Chart_AT/%s.bundle" % key, "wb") as f:
                f.write(bundle.read())
    elif types.getboolean("illustrationBlur") and key[-23:] == ".0/IllustrationBlur.png":
        key = key[:-23]
        with apk.open("assets/aa/Android/%s" % entry) as bundle:
            with open("illustrationBlur/%s.bundle" % key, "wb") as f:
                f.write(bundle.read())
    elif types.getboolean("illustrationLowRes") and key[-25:] == ".0/IllustrationLowRes.png":
        key = key[:-25]
        with apk.open("assets/aa/Android/%s" % entry) as bundle:
            with open("illustrationLowRes/%s.bundle" % key, "wb") as f:
                f.write(bundle.read())
    elif types.getboolean("illustration") and key[-19:] == ".0/Illustration.png":
        key = key[:-19]
        with apk.open("assets/aa/Android/%s" % entry) as bundle:
            with open("illustration/%s.bundle" % key, "wb") as f:
                f.write(bundle.read())
    elif types.getboolean("music") and key[-12:] == ".0/music.wav":
        key = key[:-12]
        with apk.open("assets/aa/Android/%s" % entry) as bundle:
            with open("music/%s.bundle" % key, "wb") as f:
                f.write(bundle.read())

update = config["UPDATE"]
if update.getint("main_story") == 0 and update.getint("other_song") == 0 and update.getint("side_story") == 0:
    with ZipFile(sys.argv[1]) as apk:
        for key, entry in table:
            if type(key) == int:
                continue
            elif key[:7] == "avatar.":
                save_compress(key,table[entry][0])
            elif key[:14] == "Assets/Tracks/" and key[14] != "#":
                save_compress(key[14:], table[entry][0])
else:
    l = []
    with open("difficulty.csv") as f:
        line = f.readline()
        while line:
            l.append(line.split(",", 2)[0])
            line = f.readline()
    index1 = l.index("Doppelganger.LeaF")
    index2 = l.index("Poseidon.1112vsStar")
    del l[index2:len(l) - update.getint("side_story")]
    del l[index1:index2 - update.getint("other_song")]
    del l[:index1 - update.getint("main_story")]
    print(l)
    with ZipFile(sys.argv[1]) as apk:
        for key, entry in table:
            if type(key) == int:
                continue
            elif key[:7] == "avatar.":
                save_compress(key,table[entry][0])
                continue
            for id in l:
                if key.startswith("Assets/Tracks/%s.0/" % id):
                    save_compress(key[14:], table[entry][0])
                    break
