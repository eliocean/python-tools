#!/bin/python3
# exp: ./cpu_top_monitor.py 1 0.7
import sys
import os
import sys
import time

localtime = time.localtime(time.time())
log_file = "./cpu_monitor{}-{}-{}.log".format(localtime.tm_year, localtime.tm_mon, localtime.tm_mday)

Load_Average_type = 1  # 默认
TOP_Load_Average = 0.7  # 默认
if len(sys.argv) == 3:
    try:
        Load_Average_type = int(sys.argv[1])
        TOP_Load_Average = float(sys.argv[2])
    except Exception as e:
        print('参数错误, ./cpu_top_monitor.py Load_Average_type(1,5,15) TOP_Load_Average(0.7)')
        sys.exit(-1)

time_str = "[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "]"
print(time_str)

# cpu 负载
Load_Average_1 = os.popen("uptime | awk -F ': ' '{print $NF}' | awk -F ', ' '{print $1}'").read().strip()
Load_Average_5 = os.popen("uptime | awk -F ': ' '{print $NF}' | awk -F ', ' '{print $2}'").read().strip()
Load_Average_15 = os.popen("uptime | awk -F ': ' '{print $NF}' | awk -F ', ' '{print $3}'").read().strip()

# cpu核数
cpu_kernel_count = float(os.popen("grep 'model name' /proc/cpuinfo | wc -l").read().strip())

if Load_Average_type == 15:
    Load_Average_calc = float(Load_Average_15) / cpu_kernel_count

elif Load_Average_type == 5:
    Load_Average_calc = float(Load_Average_5) / cpu_kernel_count

else:
    Load_Average_calc = float(Load_Average_1) / cpu_kernel_count  # 默认

print("Load_Average_1:", Load_Average_1)
print("Load_Average_5:", Load_Average_5)
print("Load_Average_15:", Load_Average_15)
print("cpu_kernel_count:", cpu_kernel_count)
print("TOP_Load_Average:", TOP_Load_Average)
print("Load_Average_calc[Load_Average/cpu_kernel_count]:", Load_Average_calc)

if Load_Average_calc >= TOP_Load_Average:
    print("Load_Average_{}超载告警!!!".format(Load_Average_type))
    with open(log_file, mode="a", encoding="utf-8") as fw:
        str_to_file = time_str + "\nLoad_Average_{}超载告警!!!\n".format(Load_Average_type)
        str_to_file = str_to_file + "Load_Average_1: {}\nLoad_Average_5: {}\nLoad_Average_15: {}\n".format(
            Load_Average_1, Load_Average_5, Load_Average_15)
        str_to_file = str_to_file + "cpu_kernel_count: {}\nTOP_Load_Average: {}\nLoad_Average_calc: {}\n".format(
            cpu_kernel_count, TOP_Load_Average, Load_Average_calc)
        str_to_file = str_to_file + "\npid,pcpu,cmd\n"
        str_to_file = str_to_file + os.popen("ps -eo pid,pcpu,cmd | sort -r -n -k 2 | head -n 10").read()
        str_to_file = str_to_file + "\n\n"
        fw.write(str_to_file)
