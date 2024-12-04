# Phigros_Resource
本项目包含资源文件

资源包括

[信息](../../tree/info)

定数，收藏品id对应中文标题，头像id，tips

曲id，曲名，曲师，画师，谱师

[头像图片](../../tree/avatar)，
[铺面文件](../../tree/chart)，
[曲绘](../../tree/illustration)，
[模糊曲绘](../../tree/illustrationBlur)，
[低质量曲绘](../../tree/illustrationLowRes)，
[音乐文件](../../tree/music)

生成适配Phira的pez自制谱文件

# 介绍

`gameInformation.py`可从apk获取定数表，tips，收藏品id，头像id，曲id，曲名，曲师，画师，谱师

定数表输出为difficulty.tsv，收藏品输出为collection.tsv，头像输出为avatar.txt，tips输出为tips.txt，其余输出为info.tsv

`resource.py`依赖difficulty.tsv和tmp.tsv，从apk内解压出头像、谱面、曲绘、音乐资源，为png，ogg，json

phira.py依赖info.tsv，difficulty.tsv，music/，IllustrationLowRes/, Chart*/，生成phira文件夹内的自制谱文件
# 配置文件 config.ini
```ini
[TYPES]
avatar = true
chart = true
illustrationblur = true
illustrationlowres = true
illustration = true
music = true
[UPDATE]
# 主线
main_story = 0
# 单曲和合集
other_song = 0
# 支线
side_story = 0
```
TYPES section为设定你需要哪些种类的资源，见README.md开头

当UPDATE section全为0时，默认获取全部歌曲的资源

当UPDATE section不是全为0时，会通过difficulty.tsv获取最近的歌曲，当Phigros更新时使用，更新了哪个部分，更新了几首，运行resource.py时只会提取最近几首的资源
# 使用示例
## 准备环境
```shell
pkg install libjpeg-turbo //非Termux不需要这个
pip install UnityPy==1.10.18
pip install fsb5   //解压音频才需要，默认提取全部资源
pip install pyqt5
pip install pyqt5-tool
```
也可：
```
pkg install libjpeg-turbo //非Termux不需要这个
pip install requirements.txt
```
## 开始提取
### Taptap下载的apk
使用GUI:
```
python gui.py
```
使用命令行：
1. 使用Termux并安装Taptap版Phigros可自动定位apk，无需输入apk路径
2. 可以运行`python taptap.py`来获取Taptap版Phigros下载链接
```shell
git clone --depth 1 https://github.com/7aGiven/Phigros_Resource
cd Phigros_Resource
python gameInformation.py Phigros.apk
python resource.py Phigros.apk
```
### Google Play下载的apk和obb
```shell
git clone --depth 1 https://github.com/7aGiven/Phigros_Resource
cd Phigros_Resource
python gameInformation.py Phigros.apk
python resource.py Phigros.obb
```
## 生成自制谱文件s
=======
# 生成自制谱文件
`python phira.py`
