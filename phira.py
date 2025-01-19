import os
import shutil
from zipfile import ZipFile, BadZipFile

levels = ["EZ", "HD", "IN", "AT"]

# 删除旧目录并创建新目录
try:
    shutil.rmtree("phira", True)
    os.mkdir("phira")
    for level in levels:
        os.mkdir(f"phira/{level}")
except Exception as e:
    print(f"错误：创建或删除目录时出错 - {e}")
    exit(1)

# 读取并解析 info.tsv 文件
infos = {}
try:
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
except FileNotFoundError:
    print("错误：未找到 info.tsv 文件。请检查 info 目录是否存在且包含该文件。")
    exit(1)
except Exception as e:
    print(f"错误：读取 info.tsv 时出错 - {e}")
    exit(1)

# 读取并解析 difficulty.tsv 文件
try:
    with open("info/difficulty.tsv", encoding="utf8") as f:
        while True:
            line = f.readline()
            if not line:
                break
            line = line[:-1].split("\t")
            if line[0] in infos:
                infos[line[0]]["difficulty"] = line[1:]
            else:
                print(f"警告：difficulty.tsv 中的 ID {line[0]} 在 info.tsv 中未找到。")
except FileNotFoundError:
    print("错误：未找到 difficulty.tsv 文件。请检查 info 目录是否存在且包含该文件。")
    exit(1)
except Exception as e:
    print(f"错误：读取 difficulty.tsv 时出错 - {e}")
    exit(1)

# 创建 .pez 文件
for id, info in infos.items():
    try:
        print(f"正在处理：{info['Name']}，作曲者：{info['Composer']}")
        for level_index in range(len(info.get("difficulty", []))):
            level = levels[level_index]
            pez_path = f"phira/{level}/{id}-{level}.pez"
            try:
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
                    try:
                        pez.write(f"chart/{id}.0/{level}.json", f"{id}.json")
                    except FileNotFoundError:
                        print(f"警告：未找到 {id} 的 {level} 图表文件 (chart/{id}.0/{level}.json)。")

                    try:
                        pez.write(f"IllustrationLowRes/{id}.png", f"{id}.png")
                    except FileNotFoundError:
                        print(f"警告：未找到 {id} 的插图文件 (IllustrationLowRes/{id}.png)。")

                    try:
                        pez.write(f"music/{id}.ogg", f"{id}.ogg")
                    except FileNotFoundError:
                        print(f"警告：未找到 {id} 的音乐文件 (music/{id}.ogg)。")

            except BadZipFile as e:
                print(f"错误：创建 .pez 文件 {pez_path} 时出错 - {e}")
            except Exception as e:
                print(f"错误：写入 .pez 文件 {pez_path} 时出错 - {e}")

    except KeyError as e:
        print(f"错误：ID {id} 缺少必要的键 {e}。")
    except Exception as e:
        print(f"意外错误：处理 ID {id} 时发生错误 - {e}")
