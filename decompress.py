from concurrent.futures import ThreadPoolExecutor
from configparser import ConfigParser
from io import BytesIO
import os
from queue import Queue
import threading
import time
from UnityPy import Environment
from UnityPy.enums import ClassIDType
import UnityPy



os.chdir(__file__[:-13])


config_parser = ConfigParser()
config_parser.read("config.ini", "utf8")
types = config_parser["TYPES"]



queue = Queue()
def io():
    while True:
        path, resource = queue.get()
        print(path)
        if path == None:
            break
        elif type(resource) == BytesIO:
            with open(path, "wb") as f:
                f.write(resource.getbuffer())
            resource.close()
        else:
            with open(path, "wb") as f:
                f.write(resource)

def save_image(image, path):
    bytesIO = BytesIO()
    t1 = time.time()
    image.save(bytesIO, "png")
    print("%f秒" % round(time.time() - t1, 4))
    queue.put((path, bytesIO))

def save_music(music, path):
    t1 = time.time()
    queue.put((path, music.samples["music.wav"]))
    print("%f秒" % round(time.time() - t1, 4))


classes = ClassIDType.TextAsset, ClassIDType.Sprite, ClassIDType.AudioClip
def save(key, entry):
    obj = entry.get_filtered_objects(classes)
    obj = next(obj).read()
    if config["avatar"] and key[:7] == "avatar/":
        bytesIO = BytesIO()
        obj.image.save(bytesIO, "png")
        queue.put((key + "png", bytesIO))
    elif getbool("Chart") and key[:6] == "Chart_":
        queue.put((key + "json", obj.script))
    elif config["illustrationBlur"] and key[:17] == "illustrationBlur/":
        bytesIO = BytesIO()
        obj.image.save(bytesIO, "png")
        queue.put((key + "png", bytesIO))
    elif config["illustrationLowRes"] and key[:19] == "illustrationLowRes/":
        pool.submit(save_image, obj.image, key + "png")
    elif config["illustration"] and key[:13] == "illustration/":
        pool.submit(save_image, obj.image, key + "png")
    elif config["music"] and key[:6] == "music/":
        pool.submit(save_music, obj, key + "wav")
    os.remove(key + "bundle")
        


env = Environment()
thread = threading.Thread(target=io)
thread.start()
ti = time.time()
type_turple = ("avatar", "Chart_EZ", "Chart_HD", "Chart_IN", "Chart_AT", "illustrationBlur", "illustrationLowRes", "illustration", "music")
def getbool(t):
    if t[:6] == "Chart_":
        return types.getboolean("Chart")
    else:
        return types.getboolean(t)
config = {}
for t in type_turple:
    config[t] = getbool(t)
env = UnityPy.load(*filter(lambda x:getbool(x), type_turple))
with ThreadPoolExecutor(6) as pool:
    for key, entry in env.files.items():
        index = key.rindex("/")
        index = key.rfind("/", 0, index)
        save(key[index + 1:-6], entry)
queue.put((None,None))
thread.join()
print("%f秒" % round(time.time() - ti, 4))
