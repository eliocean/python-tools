#!/usr/bin/python3
# -*-coding:utf-8 -*-
import time
from socket import *

CODING = "utf-8"
HOST = '127.0.0.1'  # 服务端ip
PORT = 21566  # 服务端端口号
BUFSIZ = 1024


class Client(object):
    def __init__(self, host=HOST, port=PORT):
        """
        :param host: ip of server
        :param port: port of the server
        """
        self.tcpCliSock = socket(AF_INET, SOCK_STREAM)  # 创建socket对象
        self.tcpCliSock.connect((HOST, PORT))  # 连接服务器
        self.payload = ""  # 获取的消息暂时为空

    def send_msg(self, msg):
        # 采取一问一答的方式，服务器接受完一次发送之后，回复确认，客服端收到确认在继续传输数据
        # 连续发送两个包,可能导致包重叠到一起
        self.tcpCliSock.send(str(len('{}'.format(msg).encode(CODING))).encode(CODING))  # 发送msg的字节长度给server
        ack = self.tcpCliSock.recv(BUFSIZ).decode(CODING)
        if ("1" == ack):
            self.tcpCliSock.send(msg.encode(CODING))  # send to server
        else:
            print("sorry, server receive the size info Failed...")
            print("ack= ", ack)

    def recv_serv_msg(self):
        # 判断一下，一个命令执行后，它返回的数据到底有没有完全传输完毕，如果没有，那么就继续传输，直到传完为止
        data_size = self.tcpCliSock.recv(BUFSIZ).decode(CODING)  # 获取接收数据的字节长度
        self.tcpCliSock.send("1".encode(CODING))  # 回复确认收到字节长度信息
        try:
            while len(self.payload.encode(CODING)) < int(data_size):  # 持续接收数据
                self.payload += self.tcpCliSock.recv(BUFSIZ).decode(CODING)  # msg form server
            return self.payload
        except Exception:
            print("data_size reveive Failed :", data_size)

    def ask_server(self, msg):
        self.send_msg(msg)
        return self.recv_serv_msg()

    def __del__(self):
        self.send_msg("exit()")  # tell server to close the socket
        self.tcpCliSock.close()  # close Socket


def ask_node(ip, port, func, params=("",)):
    client = Client(ip, port)
    data = {
        "func": func,
        "params": params
    }
    return client.ask_server(str(data))


if __name__ == '__main__':
    while True:
        time.sleep(1)
        rev_text = ask_node(HOST, PORT, "get_msg", ("hello world", "my", "name", "is", "yyl"))
        print(rev_text)
