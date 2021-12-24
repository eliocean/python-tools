"""
1:raw_cookie形式如：
CURRENT_FNVAL=16
_uuid=889F05AC-3417-E6B1-B676-FF495D8B52BC32374infoc
buvid3=4BA38102-367E-478B-B2E5-22413E1DB624155819infoc
LIVE_BUVID=AUTO9315693741378918

2:header_cookies形式如：
Cookie: CURRENT_FNVAL=16; _uuid=889F05AC-3417-E6B1-B676-FF495D8B52BC32374infoc; buvid3=4BA
"""

reslist = []

select = input("选择cookie数据格式(默认2):\n1:raw_cookie\n2:header_cookies\n>>")



# 格式化一行数据，
def parseLine(line):
    res = "\"" + line.strip() + "\","
    res = res.replace("=", "\":\"")
    reslist.append(res)


if select == "2":
    print("解析header_cookies...OK")
    with open("header_cookies", encoding="utf-8") as f:
        cookies = f.read()
        cookies = cookies.replace("Cookie:"," ")
        lines = cookies.split(";")
        for line in lines:
            parseLine(line)
else:
    print("解析raw_cookies...OK")
    with open("raw_cookies", encoding="utf-8") as f:
        while True:
            line = f.readline()
            if not line:
                break
            parseLine(line)


with open("output","w",encoding="utf-8") as f2:
    f2.write("\n".join(reslist))
