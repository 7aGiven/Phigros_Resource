import re
from requests import Session

s = Session()

res = s.get("https://616.sb")
match = re.search(b"index-[^.]+", res.content)
path = match.group().decode()
print(path)

res = s.get("https://616.sb/assets/%s.js" % body)
match = re.search(b"DownloadPage-[^.]+", res.content)
path = match.group().decode()
print(path)

res = s.get("https://616.sb/assets/%s.js" % path)
body = res.text

index = body.index("Phigros")

match = re.search('n:([^,]+)', body[index:])
version = int(match.group(1))
print(version)

match = re.search('g:"([^"]+)', body[index:])
versionString = match.group(1)
print(versionString)



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
