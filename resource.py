import base64
from concurrent.futures import ThreadPoolExecutor
from configparser import ConfigParser
import gc
from io import BytesIO
import json
import os
from queue import Queue
import shutil
import sys
import threading
import time
from UnityPy import Environment
from UnityPy.enums import ClassIDType
from zipfile import ZipFile



class ByteReader:
    def __init__(self, data):
        self.data = data
        self.position = 0

    def readInt(self):
        self.position += 4
        return self.data[self.position-4]^self.data[self.position-3]<<8^self.data[self.position-2]<<16

queue_out = Queue()
queue_in = Queue()


def getbool(t):
    if t[:6] == "Chart_":
        return config["Chart"]
    else:
        return config[t]

def io():
    while True:
        item = queue_in.get()
        if item == None:
            break
        elif type(item) == list:
            env = Environment()
            for i in range(1, len(item)):
                env.load_file(item[0].read("assets/aa/Android/%s" % item[i][1]), name=item[i][0])
            queue_out.put(env)
            del env
        else:
            path, resource = item
            print(path)
            if type(resource) == BytesIO:
                with resource:
                    with open(path, "wb") as f:
                        f.write(resource.getbuffer())
            else:
                with open(path, "wb") as f:
                    f.write(resource)

def save_image(path, image):
    bytesIO = BytesIO()
    t1 = time.time()
    image.save(bytesIO, "png")
    print("%f秒" % round(time.time() - t1, 4))
    queue_in.put((path, bytesIO))

def save_music(path, music):
    t1 = time.time()
    queue_in.put((path, music.samples["music.wav"]))
    print("%f秒" % round(time.time() - t1, 4))

classes = ClassIDType.TextAsset, ClassIDType.Sprite, ClassIDType.AudioClip
def save(key, entry):
    obj = entry.get_filtered_objects(classes)
    obj = next(obj).read()
    if config["avatar"] and key[:7] == "avatar.":
        key = key[7:]
        if key != "Cipher1":
            key = avatar[key]
        bytesIO = BytesIO()
        obj.image.save(bytesIO, "png")
        queue_in.put(("avatar/%s.png" % key, bytesIO))
    elif config["Chart"] and key[-14:-7] == "/Chart_" and key[-5:] == ".json":
        queue_in.put(("Chart_%s/%s.json" % (key[-7:-5], key[:-14]), obj.script))
    elif config["IllustrationBlur"] and key[-23:] == ".0/IllustrationBlur.png":
        key = key[:-23]
        bytesIO = BytesIO()
        obj.image.save(bytesIO, "png")
        queue_in.put(("IllustrationBlur/%s.png" % key, bytesIO))
    elif config["IllustrationLowRes"] and key[-25:] == ".0/IllustrationLowRes.png":
        key = key[:-25]
        pool.submit(save_image, "IllustrationLowRes/%s.png" % key, obj.image)
    elif config["Illustration"] and key[-19:] == ".0/Illustration.png":
        key = key[:-19]
        pool.submit(save_image, "Illustration/%s.png" % key, obj.image)
    elif config["music"] and key[-12:] == ".0/music.wav":
        key = key[:-12]
        pool.submit(save_music, "music/%s.wav" % key, obj)

def run(path, c):
    global config
    config = c
    with ZipFile(path) as apk:
        with apk.open("assets/aa/catalog.json") as f:
            data = json.load(f)

    type_list = ("avatar", "Chart_EZ", "Chart_HD", "Chart_IN", "Chart_AT", "IllustrationBlur", "IllustrationLowRes", "Illustration", "music")
    for directory in filter(lambda x:getbool(x), type_list):
        shutil.rmtree(directory, True)
        os.mkdir(directory)


    key = base64.b64decode(data["m_KeyDataString"])
    bucket = base64.b64decode(data["m_BucketDataString"])
    entry = base64.b64decode(data["m_EntryDataString"])

    table = []
    reader = ByteReader(bucket)
    for x in range(reader.readInt()):
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
        for i in range(reader.readInt()):
            entry_position = reader.readInt()
            entry_value = entry[4+28*entry_position:4+28*entry_position+28]
            entry_value = entry_value[8]^entry_value[9]<<8
        table.append([key_value, entry_value])
    for i in range(len(table)):
        if table[i][1] != 65535:
            table[i][1] = table[table[i][1]][0]
    for i in range(len(table) - 1, -1, -1):
        if type(table[i][0]) == int or table[i][0][:15] == "Assets/Tracks/#" or table[i][0][:14] != "Assets/Tracks/" and table[i][0][:7] != "avatar.":
            del table[i]
        elif table[i][0][:14] == "Assets/Tracks/":
            table[i][0] = table[i][0][14:]
    for key, value in table:
        print(key, value)

                

    global avatar
    if config["avatar"]:
        avatar = {}
        with open("avatar.csv") as f:
            line = f.readline()[:-1]
            while line:
                l = line.split(",")
                avatar[l[1]] = l[0]
                line = f.readline()[:-1]

    thread = threading.Thread(target=io)
    thread.start()
    ti = time.time()
    update = config["UPDATE"]
    global pool
    with ThreadPoolExecutor(6) as pool:
        if update["main_story"] == 0 and update["other_song"] == 0 and update["side_story"] == 0:
            with ZipFile(path) as apk:
                size = 0
                l = [apk]
                for key, entry in table:
                    l.append((key, entry))
                    info = apk.getinfo("assets/aa/Android/%s" % entry)
                    size += info.file_size
                    print(size)
                    if size > 32 * 1024 * 1024:
                        queue_in.put(l)
                        env = queue_out.get()
                        for ikey, ientry in env.files.items():
                            save(ikey,ientry)
                        size = 0
                        del env
                        gc.collect()
                        l = [apk]
                queue_in.put(l)
                env = queue_out.get()
                for ikey, ientry in env.files.items():
                    save(ikey,ientry)
        else:
            l = []
            with open("difficulty.csv", encoding="utf8") as f:
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
            env = Environment()
            with ZipFile(path) as apk:
                for key, entry in table:
                    if key[:7] == "avatar.":
                        env.load_file(apk.read("assets/aa/Android/%s" % entry), name=key)
                        continue
                    for id in l:
                        if key.startswith("%s.0/" % id):
                            env.load_file(apk.read("assets/aa/Android/%s" % entry), name=key)
                            break
            for ikey, ientry in env.files.items():
                save(ikey,ientry)
    queue_in.put(None)
    thread.join()
    print("%f秒" % round(time.time() - ti, 4))
if __name__=="__main__":
    c = ConfigParser()
    c.read("config.ini", "utf8")
    types = c["TYPES"]
    run(sys.argv[1], {
        "avatar": types.getboolean("avatar"),
        "Chart": types.getboolean("Chart"),
        "IllustrationBlur": types.getboolean("illustrationBlur"),
        "IllustrationLowRes": types.getboolean("illustrationLowRes"),
        "Illustration": types.getboolean("illustration"),
        "music": types.getboolean("music"),
        "UPDATE": {
            "main_story": c["UPDATE"].getint("main_story"),
            "side_story": c["UPDATE"].getint("side_story"),
            "other_song": c["UPDATE"].getint("other_song")
        }
    })