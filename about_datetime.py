# 引入模块
import time, datetime

# 1. 打印当前时间
# datetime获取当前时间，数组格式
now = datetime.datetime.now()
now = str(now.strftime("%Y-%m-%d %H:%M:%S")) + "   星期：" + str(now.isoweekday())
print("当前时间:", now)

# time获取当前时间戳
now = int(time.time())     # 1533952277
timeArray = time.localtime(now)
print(timeArray)
styleTime = time.strftime("%Y--%m--%d %H:%M:%S", timeArray)
print(styleTime)


# 2. str类型的日期转换为时间戳
tss = '2013-11-10 23:40:01'

# 时间str转为时间数组:time.struct_time
timeArray = time.strptime(tss, "%Y-%m-%d %H:%M:%S")
print(timeArray)
# timeArray可以调用tm_year等
print("{}-{}-{} {}:{}:{} 星期:{}".format(timeArray.tm_year, timeArray.tm_mon, timeArray.tm_mday, timeArray.tm_hour,
                                       timeArray.tm_min, timeArray.tm_sec, timeArray.tm_wday))

# 时间数组转为时间戳
timeStamp = int(time.mktime(timeArray))
print(timeStamp)  # 1384098001

# 时间数组转为其它显示格式
time_s = time.strftime("%Y/%m/%d %H-%M-%S", timeArray)
print(time_s)  # 2013/11/10 23-40-01

# 3.时间戳转换为指定格式的日期
# 使用time
timeStamp = 1384098001
timeArray = time.localtime(timeStamp)
time_s = time.strftime("%Y--%m--%d %H:%M:%S", timeArray)
print(time_s)  # 2013--11--10 23:40:01

# 使用datetime
dateArray = datetime.datetime.fromtimestamp(timeStamp)
time_s = dateArray.strftime("%Y--%m--%d %H:%M:%S")
print(time_s)  # 2013--11--10 23:40:01
# 使用datetime，指定utc时间，相差8小时
dateArray = datetime.datetime.utcfromtimestamp(timeStamp)
time_s = dateArray.strftime("%Y--%m--%d %H:%M:%S")
print(time_s)  # 2013--11--10 15:40:01
