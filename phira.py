import os
import shutil
from zipfile import ZipFile

levels = ["EZ", "HD", "IN", "AT"]

# 删除旧目录并创建新目录
shutil.rmtree("phira", True)
os.mkdir("phira")
for level in levels:
    os.mkdir(f"phira/{level}")

# 读取并解析 info.tsv 文件
infos = {}
with open("info/info.tsv", encoding="utf8") as f:
    while True:
        line = f.readline()
        if not line:
            break
        line = line[:-1].split("\t")
        infos[line[0]] = {
            "Name": line[1],
            "Composer": line[2],
            "Illustrator": line[3],
            "Chater": line[4:]
        }

# 读取并解析 difficulty.tsv 文件
with open("info/difficulty.tsv", encoding="utf8") as f:
    while True:
        line = f.readline()
        if not line:
            break
        line = line[:-1].split("\t")
        infos[line[0]]["difficulty"] = line[1:]

# 创建 .pez 文件
for id, info in infos.items():
    print(info["Name"], info["Composer"])
    for level_index in range(len(info["difficulty"])):
        level = levels[level_index]
        pez_path = f"phira/{level}/{id}-{level}.pez"
        with ZipFile(pez_path, "x") as pez:
            # 写入 info.txt 内容
            info_txt_content = (
                f"#\n"
                f"Name: {info['Name']}\n"
                f"Song: {id}.ogg\n"
                f"Picture: {id}.png\n"
                f"Chart: {id}.json\n"
                f"Level: {level} Lv.{info['difficulty'][level_index]}\n"
                f"Composer: {info['Composer']}\n"
                f"Illustrator: {info['Illustrator']}\n"
                f"Charter: {info['Chater'][level_index]}"
            )
            pez.writestr("info.txt", info_txt_content)

            # 添加文件到 .pez 压缩包
            pez.write(f"chart/{id}.0/{level}.json", f"{id}.json")
            pez.write(f"IllustrationLowRes/{id}.png", f"{id}.png")
            pez.write(f"music/{id}.ogg", f"{id}.ogg")
