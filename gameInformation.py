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
        information = data.raw_data.tobytes()
    elif data.m_Script.get_obj().read().name == "GetCollectionControl":
        collection = data.raw_data.tobytes()
    elif data.m_Script.get_obj().read().name == "TipsProvider":
        tips = data.raw_data.tobytes()



position = information.index(b"\x16\x00\x00\x00Glaciaxion.SunsetRay.0\x00\x00\n")

reader = ByteReader(information[position - 4:])

def readObject():
    item = {}

    item["songsId"] = reader.readString()
    item["songsKey"] = reader.readString()
    item["songsName"] = reader.readString()
    item["songsTitle"] = reader.readString()
    
    item["difficulty"] = []
    for i in range(reader.readInt()):
        difficulty = reader.readFloat()
        if difficulty:
            item["difficulty"].append(round(difficulty,1))

    item["illustrator"] = reader.readString()

    item["charter"] = []
    for i in range(reader.readInt()):
        charter = reader.readString()
        if len(charter) != 0:
            item["charter"].append(charter)

    item["composer"] = reader.readString()
    
    item["levels"] = []
    for i in range(reader.readInt()):
        item["levels"].append(reader.readString())

    item["previewTime"] = reader.readFloat()

    unlockInfoList = []
    for x in range(reader.readInt()):
        unlockInfo = {}
        unlockType = reader.readInt()
        if not unlockType:
            reader.position += 4
            continue
        unlockInfo["unlockType"] = unlockType
        unlockInfo["unlockInfo"] = []
        for i in range(reader.readInt()):
            unlockInfo["unlockInfo"].append(reader.readString())
        unlockInfoList.append(unlockInfo)
    if unlockInfoList:
        item["unlockInfo"] = unlockInfoList


    length = reader.readInt()
    reader.position += 4 * length
    return item



difficulty = []
table = []

for i in range(reader.readInt()):
    result = readObject()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if len(result["levels"]) != 4:
        result["difficulty"].pop()
        result["charter"].pop()
    id = result["songsId"][:-2]
    difficulty.append([id] + result["difficulty"])
    table.append([id, result["songsName"], result["composer"], result["illustrator"], "\\".join(result["charter"])])

for i in range(reader.readInt()):
    result = readObject()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if len(result["levels"]) != 4:
        result["difficulty"].pop()
        result["charter"].pop()
    id = result["songsId"][:-2]
    difficulty.append([id] + result["difficulty"])
    table.append([id, result["songsName"], result["composer"], result["illustrator"], "\\".join(result["charter"])])

for i in range(reader.readInt()):
    result = readObject()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if len(result["levels"]) != 4:
        result["difficulty"].pop()
        result["charter"].pop()
    id = result["songsId"][:-2]
    difficulty.append([id] + result["difficulty"])
    table.append([id, result["songsName"], result["composer"], result["illustrator"], "\\".join(result["charter"])])

print(difficulty)
print(table)

with open("difficulty.csv", "w") as f:
    for item in difficulty:
        f.write("\\".join([str(x) for x in item]))
        f.write("\n")

with open("info.csv", "w", encoding="utf8") as f:
    for item in table:
        f.write("\\".join(item))
        f.write("\n")

reader = ByteReader(collection)
table = []
for i in range(reader.readInt()):
    reader.position += 3 * 4
    reader.skipString()
    reader.skipString()
    reader.skipString()
    key = reader.readString()
    index = reader.readInt()
    reader.position += 4
    title = reader.readString()
    reader.readString()
    reader.readString()
    reader.readString()
    reader.readString()
    if index == 1:
        table.append((key, title))

with open("collection.csv", "w") as f:
    for item in table:
        f.write(",".join(item))
        f.write("\n")

table = []
for i in range(reader.readInt()):
    reader.position += 3 * 4
    reader.skipString()
    reader.position += 4
    reader.skipString()
    key = reader.readString()
    avatar = reader.readString()
    table.append((key, avatar[7:]))

with open("avatar.txt", "w") as f:
    for item in table:
        f.write(item[0])
        f.write("\n")

with open("avatar.csv", "w") as f:
    for item in table:
        f.write(",".join(item))
        f.write("\n")

reader = ByteReader(tips)
reader.position = 8
table = []
for i in range(reader.readInt()):
    table.append(reader.readString())
with open("tips.txt", "w") as f:
    for item in table:
        f.write(item)
        f.write("\n")