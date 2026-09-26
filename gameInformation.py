import json
import os
import sys
from UnityPy import Environment
import zipfile
from io import BytesIO
from log import init_console_logger
import logging

DEBUG = False

def run(path, logger):
    Tips = None
    GameInformation = None
    Collections = None
    with open("typetree.json") as f:
        typetree = json.load(f)
    env = Environment()
    with zipfile.ZipFile(path) as apk:
        with apk.open("assets/bin/Data/globalgamemanagers.assets") as f:
            env.load_file(BytesIO(f.read()), name="assets/bin/Data/globalgamemanagers.assets")
        with apk.open("assets/bin/Data/level0") as f:
            env.load_file(BytesIO(f.read()))
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        data = obj.read()
        if data.m_Script.get_obj().read().name == "GameInformation":
            GameInformation = obj.read_typetree(typetree["GameInformation"])
        elif data.m_Script.get_obj().read().name == "GetCollectionControl":
            Collections = obj.read_typetree(typetree["GetCollectionControl"], True)
        elif data.m_Script.get_obj().read().name == "TipsProvider":
            Tips = obj.read_typetree(typetree["TipsProvider"], True)

    difficulty = []
    table = []
    for key, songs in GameInformation["song"].items():
        if key == "otherSongs":
            continue
        for song in songs:
            for i in range(len(song["difficulty"])):
                song["difficulty"][i] = str(round(song["difficulty"][i], 1))
            if song["songsName"] == "望影の方舟Six":
                difficulty.append([song["songsId"]] + song["difficulty"] + ["0.0"] + song["difficulty"])
                song["charter"].append("NULL")
                for i in range(0,3):
                    song["charter"].append(song["charter"][i])
            else:
                difficulty.append([song["songsId"]] + song["difficulty"])
            if song["songsName"] == "Random":
                a = ["","[R]","[A]","[N]","[D]","[O]","[M]"]
                charters = [
    ["Barbarianerman", "IMD_6", "_鉄"],
    ["Barbarianerman × V17AMax", "IMD_6 × JKy", "_鉄 × Rikko"],
    ["Barbarianerman × Pcat", "IMD_6 × Ctymax", "_鉄 × NerSAN"],
    ["Barbarianerman × TimiTini", "IMD_6 × Gausbon", "_鉄 × Myna"],
    ["Barbarianerman × Clutter", "IMD_6 × Uvernight", "_鉄 × Su1fuR"],
    ["Barbarianerman × 阿爽", "IMD_6 × 晨", "_鉄 × 百九十八"],
    ["Barbarianerman × J.R", "IMD_6 × Likey", "_鉄 × XMT小咩兔"]
]
                for i in range(0,7):
                    difficulty.append([song["songsId"][:-1] + str(i)] + song["difficulty"])
                    table.append((song["songsId"][:-1] + str(i), song["songsName"] + a[i], song["composer"], song["illustrator"], *charters[i]))
            else:
                table.append((song["songsId"], song["songsName"], song["composer"], song["illustrator"], *song["charter"]))

    logger.info(difficulty)
    logger.info(table)

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
    for key in GameInformation["keyStore"]:
        if key["kindOfKey"] == 0:
            single.append(key["keyName"])
        elif key["kindOfKey"] == 2 and key["keyName"] != "Introduction" and key["keyName"] not in single:
            illustration.append(key["keyName"])

    with open("info/single.txt", "w", encoding="utf8") as f:
        for item in single:
            f.write("%s\n" % item)

    with open("info/illustration.txt", "w", encoding="utf8") as f:
        for item in illustration:
            f.write("%s\n" % item)
    logger.info(single)
    logger.info(illustration)

    D = {}
    for item in Collections.collectionItems:
        if item.key in D:
            D[item.key][1] = item.subIndex
        else:
            D[item.key] = [item.multiLanguageTitle.chinese, item.subIndex]

    with open("info/collection.tsv", "w", encoding="utf8") as f:
        for key, value in D.items():
            f.write("%s\t%s\t%s\n" % (key, value[0], value[1]))

    with open("info/avatar.txt", "w", encoding="utf8") as avatar:
        with open("info/tmp.tsv", "w", encoding="utf8") as tmp:
            for item in Collections.avatars:
                avatar.write(item.name)
                avatar.write("\n")
                tmp.write("%s\t%s\n" % (item.name, item.addressableKey[7:]))

    with open("info/tips.txt", "w", encoding="utf8") as f:
        for tip in Tips.tips[0].tips:
            f.write(tip)
            f.write("\n")


if __name__ == "__main__":
    if len(sys.argv) == 1 and os.path.isdir("/data/"):
        import subprocess
        r = subprocess.run("pm path com.PigeonGames.Phigros",stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,shell=True)
        file_path = r.stdout[8:-1].decode()
    else:
        file_path = sys.argv[1]
    if not os.path.isdir("info"):
        os.mkdir("info")
    run(file_path, init_console_logger())
