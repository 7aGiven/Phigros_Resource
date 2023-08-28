from requests import Session
import sys

s = Session()

# res = requests.get("https://616.sb/assets/DownloadPage-a78f0b44.js")
# print(res.text)

versionString = sys.argv[1]

version = int(sys.argv[2])

res = s.get("https://load-balance.minasan.xyz/com.PigeonGames.Phigros/com.PigeonGames.Phigros_%s.apk" % versionString, stream=True)
length = int(res.headers["Content-Length"]) / 1024 / 1024
print(length, "MB")
progress = 0
with open("Phigros.apk", "wb") as f:
    for data in res.iter_content(1024 * 1024):
        progress += 1
        print("\r%dMB/%.2fMB" % (progress, length), end="")
        f.write(data)
print("")

res = s.get("https://load-balance.minasan.xyz/com.PigeonGames.Phigros/main.%d.com.PigeonGames.Phigros.obb" % version, stream=True)
length = int(res.headers["Content-Length"]) / 1024 / 1024
print(length, "MB")
progress = 0
with open("Phigros.obb", "wb") as f:
    for data in res.iter_content(1024 * 1024):
        progress += 1
        print("\r%dMB/%.2fMB" % (progress, length), end="")
        f.write(data)
