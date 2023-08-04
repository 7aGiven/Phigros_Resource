from concurrent.futures import ThreadPoolExecutor
from configparser import ConfigParser
from io import BytesIO
import gc
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


queue_load = Queue()
queue = Queue()
def io():
    while True:
        item = queue.get()
        if item == None:
            break
        elif type(item) == str:
            queue_load.put(UnityPy.load(item))
        else:
            path, resource, format = item
            print(path)
            if type(resource) == BytesIO:
                with open(path + format, "wb") as f:
                    f.write(resource.getbuffer())
                resource.close()
            else:
                with open(path, "wb") as f:
                    f.write(resource)
            os.remove(path + "bundle")

def save_image(image, path):
    bytesIO = BytesIO()
    t1 = time.time()
    image.save(bytesIO, "png")
    print("%f秒" % round(time.time() - t1, 4))
    queue.put((path, bytesIO, "png"))

def save_music(music, path):
    t1 = time.time()
    queue.put((path, music.samples["music.wav"], "wav"))
    print("%f秒" % round(time.time() - t1, 4))


classes = ClassIDType.TextAsset, ClassIDType.Sprite, ClassIDType.AudioClip
def save(key, entry):
    obj = entry.get_filtered_objects(classes)
    obj = next(obj).read()
    if config["avatar"] and key[:7] == "avatar/":
        bytesIO = BytesIO()
        obj.image.save(bytesIO, "png")
        queue.put((key, bytesIO, "png"))
    elif getbool("Chart") and key[:6] == "Chart_":
        queue.put((key, obj.script, "json"))
    elif config["illustrationBlur"] and key[:17] == "illustrationBlur/":
        bytesIO = BytesIO()
        obj.image.save(bytesIO, "png")
        queue.put((key, bytesIO, "png"))
    elif config["illustrationLowRes"] and key[:19] == "illustrationLowRes/":
        pool.submit(save_image, obj.image, key)
    elif config["illustration"] and key[:13] == "illustration/":
        pool.submit(save_image, obj.image, key)
    elif config["music"] and key[:6] == "music/":
        pool.submit(save_music, obj, key)
        


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
with ThreadPoolExecutor(6) as pool:
    for dir in filter(lambda x:getbool(x), type_turple):
        queue.put(dir)
        env = queue_load.get()
        for key, entry in env.files.items():
            index = key.rindex("/")
            index = key.rfind("/", 0, index)
            save(key[index + 1:-6], entry)
        del entry
        del env
        gc.collect()
queue.put(None)
thread.join()
print("%f秒" % round(time.time() - ti, 4))
