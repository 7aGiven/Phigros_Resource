import os
import struct
import sys
from UnityPy import Environment
import zipfile

import h

class ByteReader:
    def __init__(self, data: bytes):
        self.data = data
        self.position = 0
        self.d = {bool: self.readBool, int: self.readInt, float: self.readFloat, str: self.readString}
    
    def readBool(self):
        self.position += 4
        return self.data[self.position - 4] == 0

    def readInt(self):
        self.position += 4
        return self.data[self.position - 4] ^ self.data[self.position - 3] << 8

    def readFloat(self):
        self.position += 4
        return struct.unpack("f", self.data[self.position - 4:self.position])[0]

    def readString(self):
        length = self.readInt()
        result = self.data[self.position:self.position + length].decode()
        self.position += length // 4 * 4
        if length % 4 != 0:
            self.position += 4
        return result
    
    def readClass(self, clazz):
        obj = clazz()
        for key, t in clazz.__annotations__.items():
            if not __debug__:
                print(key, t)
            if type(t) == type:
                if t in (bool, int, float, str):
                    setattr(obj, key, self.d[t]())
                else:
                    setattr(obj, key, self.readClass(t))
            else:
                l = []
                t = t.__args__[0]
                for _ in range(self.readInt()):
                    if t in (bool, int, float, str):
                        l.append(self.d[t]())
                    else:
                        l.append(self.readClass(t))
                setattr(obj, key, l)
            if not __debug__:
                print(key, getattr(obj, key))
        return obj



def run(path):
    env = Environment()
    with zipfile.ZipFile(path) as apk:
        with apk.open("assets/bin/Data/globalgamemanagers.assets") as f:
            env.load_file(f.read(), name="assets/bin/Data/globalgamemanagers.assets")
        with apk.open("assets/bin/Data/level0") as f:
            env.load_file(f.read())
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        data = obj.read()
        if data.m_Script.get_obj().read().name == "GameInformation":
            information = data.raw_data.tobytes()
        elif data.m_Script.get_obj().read().name == "GetCollectionControl":
            collection = data.raw_data.tobytes()
        elif data.m_Script.get_obj().read().name == "TipsProvider":
            tips = data.raw_data.tobytes()
    if not __debug__:
        with open("GameInformation", "wb") as f:
            f.write(information)
        with open("GetCollectionControl", "wb") as f:
            f.write(collection)

    reader = ByteReader(information)
    reader.position = information.index(b"\x16\x00\x00\x00Glaciaxion.SunsetRay.0\x00\x00\n") - 4

    difficulty = []
    table = []
    for i in range(3):
        for ii in range(reader.readInt()):
            songItem = reader.readClass(h.SongsItem)
            songItem.songId = songItem.songId[:-2]
            if len(songItem.difficulty) == 5:
                songItem.difficulty.pop()
                songItem.charter.pop()
            if songItem.difficulty[-1] == 0.0:
                songItem.difficulty.pop()
                songItem.charter.pop()
            for i in range(len(songItem.difficulty)):
                songItem.difficulty[i] = str(round(songItem.difficulty[i], 1))
            difficulty.append([songItem.songsId]+songItem.difficulty)
            table.append((songItem.songsId, songItem.songsName, songItem.composer, songItem.illustrator, *songItem.charter))
    for i in range(reader.readInt()):
        reader.readClass(h.SongsItem)

    print(difficulty)
    print(table)

    with open("info/difficulty.tsv", "w", encoding="utf8") as f:
        for item in difficulty:
            f.write("\t".join(map(str, item)))
            f.write("\n")

    with open("info/info.tsv", "w", encoding="utf8") as f:
        for item in table:
            f.write("\t".join(item))
            f.write("\n")

    single = []
    illustration = []
    for i in range(reader.readInt()):
        key = reader.readClass(h.Key)
        if key.kindOfKey == 0:
            single.append(key.keyName)
        elif key.kindOfKey == 2 and key.keyName != "Introduction" and key.keyName not in single:
            illustration.append(key.keyName)

    with open("info/single.txt", "w", encoding="utf8") as f:
        for item in single:
            f.write("%s\n" % item)

    with open("info/illustration.txt", "w", encoding="utf8") as f:
        for item in illustration:
            f.write("%s\n" % item)
    print(single)
    print(illustration)

    reader = ByteReader(collection)

    D = {}
    for i in range(reader.readInt()):
        item = reader.readClass(h.CollectionItemIndex)
        if item.key in D:
            D[item.key][1] = item.subIndex
        else:
            D[item.key] = [item.multiLanguageTitle.chinese, item.subIndex]

    with open("info/collection.tsv", "w", encoding="utf8") as f:
        for key, value in D.items():
            f.write("%s\t%s\t%s\n" % (key, value[0], value[1]))

    with open("info/avatar.txt", "w", encoding="utf8") as avatar:
        with open("info/tmp.tsv", "w", encoding="utf8") as tmp:
            for i in range(reader.readInt()):
                item = reader.readClass(h.AvatarInfo)
                avatar.write(item.name)
                avatar.write("\n")
                tmp.write("%s\t%s\n" % (item.name, item.addressableKey[7:]))

    reader = ByteReader(tips[8:])

    with open("info/tips.txt", "w", encoding="utf8") as f:
        for i in range(reader.readInt()):
            f.write(reader.readString())
            f.write("\n")


if __name__ == "__main__":
    if len(sys.argv) == 1 and os.path.isdir("/data/"):
        import subprocess
        r = subprocess.run("pm path com.PigeonGames.Phigros",stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,shell=True)
        path = r.stdout[8:-1].decode()
    else:
        path = sys.argv[1]
    if not os.path.isdir("info"):
        os.mkdir("info")
    run(path)
