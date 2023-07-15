import zipfile
from UnityPy import Environment
import sys
import struct
import json



class ByteReader:
    def __init__(self, data:bytes):
        self.data = data
        self.position = 0

    def readInt(self):
        self.position += 4
        return self.data[self.position - 4]
    
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



env = Environment()
with zipfile.ZipFile(sys.argv[1]) as apk:
    with apk.open("assets/bin/Data/globalgamemanagers.assets") as f:
        env.load_file(f.read(), name="assets/bin/Data/globalgamemanagers.assets")
    with apk.open("assets/bin/Data/level0") as f:
        env.load_file(f.read())
        for obj in env.objects:
            if obj.type.name != "MonoBehaviour":
                continue
            data = obj.read()
            if data.m_Script.get_obj().read().name == "GameInformation":
                data = data.raw_data.tobytes()
                break



position = data.index(b"\x16\x00\x00\x00Glaciaxion.SunsetRay.0\x00\x00\n")

byteReader = ByteReader(data[position - 4:])

def readObject():
    item = {}

    item["songsId"] = byteReader.readString()
    item["songsKey"] = byteReader.readString()
    item["songsName"] = byteReader.readString()
    item["songsTitle"] = byteReader.readString()
    
    item["difficulty"] = []
    for i in range(byteReader.readInt()):
        difficulty = byteReader.readFloat()
        if difficulty:
            item["difficulty"].append(round(difficulty,1))

    item["illustrator"] = byteReader.readString()

    item["charter"] = []
    for i in range(byteReader.readInt()):
        charter = byteReader.readString()
        if len(charter) != 0:
            item["charter"].append(charter)

    item["composer"] = byteReader.readString()
    
    item["levels"] = []
    for i in range(byteReader.readInt()):
        item["levels"].append(byteReader.readString())

    item["previewTime"] = byteReader.readFloat()

    unlockInfoList = []
    for x in range(byteReader.readInt()):
        unlockInfo = {}
        unlockType = byteReader.readInt()
        if not unlockType:
            byteReader.position += 4
            continue
        unlockInfo["unlockType"] = unlockType
        unlockInfo["unlockInfo"] = []
        for i in range(byteReader.readInt()):
            unlockInfo["unlockInfo"].append(byteReader.readString())
        unlockInfoList.append(unlockInfo)
    if unlockInfoList:
        item["unlockInfo"] = unlockInfoList


    length = byteReader.readInt()
    byteReader.position += 4 * length
    return item



difficulty = []
table = []

for i in range(byteReader.readInt()):
    result = readObject()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    id = result["songsId"][:-2]
    difficulty.append([id] + result["difficulty"])
    table.append([id, result["songsName"], result["composer"], result["illustrator"], "\\".join(result["charter"])])

for i in range(byteReader.readInt()):
    result = readObject()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    id = result["songsId"][:-2]
    difficulty.append([id] + result["difficulty"])
    table.append([id, result["songsName"], result["composer"], result["illustrator"], "\\".join(result["charter"])])

for i in range(byteReader.readInt()):
    result = readObject()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    id = result["songsId"][:-2]
    difficulty.append([id] + result["difficulty"])
    table.append([id, result["songsName"], result["composer"], result["illustrator"], "\\".join(result["charter"])])

print(difficulty)
print(table)

with open("difficulty.csv", "w") as f:
    for item in difficulty:
        f.write(",".join([str(x) for x in item]))
        f.write("\n")

with open("info.csv", "w") as f:
    for item in table:
        f.write("\\".join(item))
        f.write("\n")