import hashlib
import json
import random
import string
import time
import urllib.parse
import urllib.request
import uuid

sample = string.ascii_lowercase + string.digits

def taptap(apkid):
    nonce = "".join(random.sample(sample, 5))
    uid = uuid.uuid4()
    t = int(time.time())
    X_UA = "V=1&PN=TapTap&VN_CODE=206012000&LOC=CN&LANG=zh_CN&CH=default&UID=%s" % uid
    byte = "X-UA=%s&end_point=d1&id=%d&node=%s&nonce=%s&time=%sPeCkE6Fu0B10Vm9BKfPfANwCUAn5POcs" % (X_UA, apkid, uid, nonce, t)
    md5 = hashlib.md5(byte.encode()).hexdigest()
    body = "sign=%s&node=%s&time=%s&id=%d&nonce=%s&end_point=d1" % (md5, uid, t, apkid, nonce)
    req = urllib.request.Request(
        "https://api.taptapdada.com/apk/v1/detail?X-UA=" + urllib.parse.quote(X_UA),
        body.encode(),
        {"User-Agent": "okhttp/3.12.1"}
    )
    with urllib.request.urlopen(req) as response:
        return json.load(response)


# Phigros apk id = 926396
if __name__ == "__main__":
    r = taptap(926396)
    print(r)
