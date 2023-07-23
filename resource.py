import base64
from configparser import ConfigParser
import json
import os
import shutil
import sys
from zipfile import ZipFile



os.chdir(__file__[:-11])

config = ConfigParser()
config.read("config.ini", "utf8")
types = config["TYPES"]
type_list = ("avatar", "Chart_EZ", "Chart_HD", "Chart_IN", "Chart_AT", "illustrationBlur", "illustrationLowRes", "illustration", "music")

def getbool(t):
    if t[:6] == "Chart_":
        return types.getboolean("Chart")
    else:
        return types.getboolean(t)


with ZipFile(sys.argv[1]) as apk:
    with apk.open("assets/aa/catalog.json") as f:
        data = json.load(f)


for directory in filter(lambda x:getbool(x), type_list):
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
        if key != "Cipher1":
            key = avatar[key]
        with apk.open("assets/aa/Android/%s" % entry) as bundle:
            with open("avatar/%s.bundle" % key, "wb") as f:
                f.write(bundle.read())
    elif types.getboolean("Chart") and key[-14:-7] == "/Chart_" and key[-5:] == ".json":
        key = key[:-5]
        with apk.open("assets/aa/Android/%s" % entry) as bundle:
            with open("Chart_%s/%s.bundle" % (key[-2:], key[:-9]), "wb") as f:
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

if types.getboolean("avatar"):
    avatar = {}
    with open("avatar.csv") as f:
        line = f.readline()[:-1]
        while line:
            l = line.split(",")
            avatar[l[1]] = l[0]
            line = f.readline()[:-1]
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
