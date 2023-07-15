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
config_parser.read("config.ini")
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
        key = key[:-6]
        bytesIO = BytesIO()
        obj.image.save(bytesIO, "png")
        queue.put((key + "png", bytesIO))
    elif config["Chart_EZ"] and key[:9] == "Chart_EZ/":
        key = key[:-6]
        queue.put((key + "json", obj.script))
    elif config["Chart_HD"] and key[:9] == "Chart_HD/":
        key = key[:-6]
        queue.put((key + "json", obj.script))
    elif config["Chart_IN"] and key[:9] == "Chart_IN/":
        key = key[:-6]
        queue.put((key + "json", obj.script))
    elif config["Chart_AT"] and key[:9] == "Chart_AT/":
        key = key[:-6]
        queue.put((key + "json", obj.script))
    elif config["illustrationBlur"] and key[:17] == "illustrationBlur/":
        key = key[:-6]
        bytesIO = BytesIO()
        obj.image.save(bytesIO, "png")
        queue.put((key + "png", bytesIO))
    elif config["illustrationLowRes"] and key[:19] == "illustrationLowRes/":
        key = key[:-6]
        pool.submit(save_image, obj.image, key + "png")
    elif config["illustration"] and key[:13] == "illustration/":
        key = key[:-6]
        pool.submit(save_image, obj.image, key + "png")
    elif config["music"] and key[:6] == "music/":
        key = key[:-6]
        pool.submit(save_music, obj, key + "wav")
    os.remove(key + "bundle")
        


env = Environment()
thread = threading.Thread(target=io)
thread.start()
t = time.time()
type_turple = ("avatar", "Chart_EZ", "Chart_HD", "Chart_IN", "Chart_AT", "illustrationBlur", "illustrationLowRes", "illustration", "music")
config = {}
for t in type_turple:
    config[t] = types.getboolean(t)
env = UnityPy.load(*filter(lambda x:types.getboolean(x), type_turple))
with ThreadPoolExecutor(6) as pool:
    for key, entry in env.files.items():
        save(key, entry)
queue.put((None,None))
thread.join()
print("%f秒" % round(time.time() - t, 4))
