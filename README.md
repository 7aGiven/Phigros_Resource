# PhigrosLibrary_Resource
本项目使用Github Actions自动更新定数表和曲绘
# 介绍

`/version.txt`为Phigros版本，有作为版本检查更新意图

`/difficulty.csv`为定数表

`illustrationLowRes`内为曲绘的低质量版

# 使用示例
```shell
rm -r /tmp/Phigros_Resource
git clone https://github.com/7aGiven/PhigrosLibrary_Resource/ /tmp/Phigros_Resource

mv /tmp/Phigros_Resource/difficulty.csv .
rm -r illustrationLowRes
mv /tmp/Phigros_Resource/illustrationLowRes .
rm -rf /tmp/Phigros_Resource
```
