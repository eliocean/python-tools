from multiprocessing import Process
import threading
import gevent
import gevent.pool
import gevent.monkey

import os
import time

gevent.monkey.patch_all()
# 2个进程，3个线程，4个协程 = 2*3*4=24

def do(name):
    print("进程id:",os.getpid(),"线程id:",threading.current_thread().getName(),"done:",name)
    time.sleep(1)

# 测试ok
def fun_event(list):
    mypool = gevent.pool.Pool(4)  # 最大并发4个
    for i in range(3):
        for name in list[i:len(list):3]:
            mypool.map(do,(name,))


sem = threading.Semaphore(3) # 并发数3
def fun_thread(list):
    threadslist = []
    for i in range(3):
        part_list = list[i:len(list):3]
        mytd = threading.Thread(target=fun_event, args=(part_list,))
        mytd.start()
        threadslist.append(mytd)

    for td in threadslist:
        td.join()

def fun_process(list):
    processlist = []
    for i in range(2):
        part_list = list[i:len(list):3]
        myprocess = Process(target=fun_thread, args=(part_list,))
        myprocess.start()
        processlist.append(myprocess)

    for p in processlist:
        p.join()


if __name__ == '__main__':
    list = [i for i in range(100)]
    fun_process(list)
