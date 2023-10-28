import json
import struct
import sys
from UnityPy import Environment
import zipfile



class ByteReader:
    def __init__(self, data:bytes):
        self.data = data
        self.position = 0
        self.d = {int: self.readInt, float: self.readFloat, str: self.readString}

    def readInt(self):
        self.position += 4
        return self.data[self.position - 4] ^ self.data[self.position - 3] << 8
    
    def readFloat(self):
        self.position += 4
        return struct.unpack("f", self.data[self.position - 4:self.position])[0]

    def readString(self):
        length = self.readInt()
        result = self.data[self.position:self.position+length].decode()
        self.position += length // 4 * 4
        if length % 4 != 0:
            self.position += 4
        return result
    
    def skipString(self):
        length = self.readInt()
        self.position += length // 4 * 4
        if length % 4 != 0:
            self.position += 4
    
    def readSchema(self, schema: dict):
        result = []
        for x in range(self.readInt()):
            item = {}
            for key, value in schema.items():
                if value in (int, str, float):
                    item[key] = self.d[value]()
                elif type(value) == list:
                    l = []
                    for i in range(self.readInt()):
                        l.append(self.d[value[0]]())
                    item[key] = l
                elif type(value) == tuple:
                    for t in value:
                        self.d[t]()
                elif type(value) == dict:
                    item[key] = self.readSchema(value)
                else:
                    raise Exception("无")
            result.append(item)
        return result

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



    reader = ByteReader(information)
    reader.position = information.index(b"\x16\x00\x00\x00Glaciaxion.SunsetRay.0\x00\x00\n") - 4
    songBase_schema = {"songId": str, "songKey": str, "songName": str, "songTitle": str, "difficulty": [float], "illustrator": str, "charter": [str], "composer": str, "levels": [str], "previewTime": float, "unlockList": {"unlockType": int, "unlockInfo": [str]}, "levelMods": {"n": [str]}}
    difficulty = []
    table = []
    for i in range(3):
        for item in reader.readSchema(songBase_schema):
            item["songId"] = item["songId"][:-2]
            if len(item["levels"]) == 5:
                item["difficulty"].pop()
                item["charter"].pop()
            if item["difficulty"][-1] == 0:
                item["difficulty"].pop()
                item["charter"].pop()
            for i in range(len(item["difficulty"])):
                item["difficulty"][i] = round(item["difficulty"][i], 1)
            difficulty.append([item["songId"]] + item["difficulty"])
            table.append((item["songId"], item["songName"], item["composer"], item["illustrator"], *item["charter"]))
    reader.readSchema(songBase_schema)

    print(difficulty)
    print(table)

    with open("difficulty.csv", "w", encoding="utf8") as f:
        for item in difficulty:
            f.write(",".join(map(str, item)))
            f.write("\n")

    with open("info.csv", "w", encoding="utf8") as f:
        for item in table:
            f.write("\\".join(item))
            f.write("\n")

    key_schema = {"key": str, "a": int, "type": int, "b": int}
    single = []
    illustration = []
    for item in reader.readSchema(key_schema):
        if item["type"] == 0:
            single.append(item["key"])
        elif item["type"] == 2 and item["key"] != "Introduction" and item["key"] not in single:
            illustration.append(item["key"])
    with open("single.txt", "w", encoding="utf8") as f:
        for item in single:
            f.write("%s\n" % item)
    with open("illustration.txt", "w", encoding="utf8") as f:
        for item in illustration:
            f.write("%s\n" % item)

    reader = ByteReader(collection)
    collection_schema = {1: (int, int, int, str, str, str), "key": str, "index": int, 2: (int,), "title": str, 3: (str, str, str, str)}
    D = {}
    for item in reader.readSchema(collection_schema):
        if item["key"] in D:
            D[item["key"]][1] = item["index"]
        else:
            D[item["key"]] = [item["title"], item["index"]]
    with open("collection.csv", "w", encoding="utf8") as f:
        for key, value in D.items():
            f.write("%s,%s,%s\n" % (key, value[0], value[1]))

    avatar_schema = {1: (int, int, int, str, int, str), "id": str, "file": str}
    table = reader.readSchema(avatar_schema)
    with open("avatar.txt", "w", encoding="utf8") as f:
        for item in table:
            f.write(item["id"])
            f.write("\n")
    with open("avatar.csv", "w") as f:
        for item in table:
            f.write("%s,%s\n" % (item["id"], item["file"][7:]))

    reader = ByteReader(tips[8:])
    with open("tips.txt", "w", encoding="utf8") as f:
        for i in range(reader.readInt()):
            f.write(reader.readString())
            f.write("\n")
            
if __name__=="__main__":
    run(sys.argv[1])