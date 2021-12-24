import requests

# 返回本机ip的接口API有很多
# https://www.xxorg.com/tools/getip/
# http://ip.3322.org/
# http://icanhazip.com/
# http://whatismyip.akamai.com/
myip = requests.get("https://www.xxorg.com/tools/getip/").text
print("ip:{}".format(myip))


# 几个免费IP地址查询接口(API)
ip126_link = "http://ip.ws.126.net/ipquery?ip={}" #126 IP API
# sina_link = "http://int.dpool.sina.com.cn/iplookup/iplookup.php?format=js&ip={}" # 新浪
ipaddr = requests.get(ip126_link.format(myip)).text
print("IPaddr:{}".format(ipaddr))
