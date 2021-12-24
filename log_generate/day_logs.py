# -*- coding:utf-8 -*-
# 基于时间保存日志，使用 TimedRotatingFileHandler
"""
TimedRotatingFileHandler的构造函数定义如下:
TimedRotatingFileHandler(filename [,when [,interval [,backupCount]]])
filename 是输出日志文件名的前缀，比如log/myapp.log_generate
when 是一个字符串的定义如下：
“S”: Seconds
“M”: Minutes
“H”: Hours
“D”: Days
“W”: Week day (0=Monday)
“midnight”: Roll over at midnight
interval 是指等待多少个单位when的时间后，Logger会自动重建文件，当然，这个文件的创建
取决于filename+suffix，若这个文件跟之前的文件有重名，则会自动覆盖掉以前的文件，所以
有些情况suffix要定义的不能因为when而重复。
backupCount 是保留日志个数。默认的0是不会自动删除掉日志。若设3，则在文件的创建过程中
库会判断是否有超过这个3，若超过，则会从最先创建的开始删除。

https://blog.csdn.net/huxiangen/article/details/86687401
"""
import logging.handlers
import time
import datetime

# logging初始化工作
logging.basicConfig()


myLog = logging.getLogger('myLog')
myLog.setLevel(logging.INFO)

# 添加TimedRotatingFileHandler
# 定义一个1分钟换一次log保存文件的handler
# 保留4个回滚文件,加上test.log总共保留5个日志文件,若超过，则test.log会被覆盖,而回滚文件会从最先创建的开始删除。
filehandler = logging.handlers.TimedRotatingFileHandler(filename="./test.log",when='M', interval=1, backupCount=4)
# 设置后缀名称，跟strftime的格式一样  when设置的是S这个结尾必须是S.log_generate
filehandler.suffix = "%Y-%m-%d_%H-%M.log_generate"
myLog.addHandler(filehandler)

while True:
	myLog.info(datetime.datetime.now())
	time.sleep(10)