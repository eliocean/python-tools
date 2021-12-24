# 基于Socket的远程调用函数(传递函数名和参数)
## client.py
客户端程序  

## Server_thread.py
server 是一个线程  
server 循环等待客户端连接,建立连接后新建一个线程.根据client传递来的参数调用Controller中的函数  
server 接收到来自客户端的"exit()"消息时,关闭客户端socket,继续等待其他客户端连接


## Controller.py
支持远程调用的函数卸载这个类里  

