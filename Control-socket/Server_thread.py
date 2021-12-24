#encoding=utf-8
#tcp-server 多线程

from socket import *
import threading
import time
from Controller import Controller
import ast

MAX_TO_CONN = 3
BUFSIZ = 1024
CODING = 'utf-8'
HOST='127.0.0.1'
PORT=21566

class Server(threading.Thread):

    def __init__(self, host=HOST, port=PORT):
        """
        :param host: ip of server
        :param port: port of the server
        """
        super().__init__()
        self.serv_host = host
        self.serv_port = port
        self.tcpS = socket(AF_INET, SOCK_STREAM)  # 创建socket对象
        self.tcpS.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # 加入socket配置，重用ip和端口
        self.tcpS.bind((host,port))  # 绑定ip端口号
        self.tcpS.listen(MAX_TO_CONN)  # 设置最大链接数
        self.controller = Controller()

    def deal_client(self,conn, addr):

        def __send_client_msg(send_msg):
            conn.send(str(len('{}'.format(send_msg).encode(CODING))).encode(CODING))  # 发送msg的字节长度给已链接客户端
            ack = conn.recv(BUFSIZ).decode(CODING)
            if ("1" == ack):
                conn.send(send_msg.encode(CODING))  # 发送消息给已链接客户端
            else:
                print("sorry, client receive the size info Failed...")
                print("ack = ",ack)


        def __recv_client_msg():
            data = ""
            data_size = conn.recv(BUFSIZ).decode(CODING)  # 获取接收数据的字节长度
            conn.send("1".encode(CODING)) # 回复确认收到字节长度信息
            try:
                while len(data.encode(CODING)) < int(data_size):  # 持续接收数据
                    data += conn.recv(BUFSIZ).decode(CODING)  # msg form server
                return data
            except Exception as e:
                print(e)


        while True:
            try:
                data = __recv_client_msg()
            except Exception as e:
                print("error while receive from client {},close the socket\n".format(addr))
                print("error: ",e)
                break
            else:
                if data == "exit()":
                    print("receive exit() form {},close the socket\n".format(addr))
                    break
                msg = '{} server receive context from {}:>{}'.format(time.strftime("%Y-%m-%d %X"),addr, data)
                print(msg)

                dict_msg = ast.literal_eval(data)
                """
                ast.literal_eval(data)
                Safely evaluate an expression node or a string containing a Python expression.
                The string or node provided may only consist of the following Python literal structures: 
                strings, bytes, numbers, tuples, lists, dicts,sets, booleans, and None.
                """
                func = getattr(self.controller,dict_msg['func'])
                __send_client_msg(func(dict_msg["params"]))
        conn.close()  # 关闭客户端链接

    def run(self):
        print("server start success，listening...")
        while True:
            conn, addr = self.tcpS.accept()
            print("add client->", addr)
            client = threading.Thread(target=self.deal_client, args=(conn, addr))
            client.start()

    def __del__(self):
        self.tcpS.close()




if __name__ == '__main__':
    serv = Server()
    serv.start()
    # import os
    # os.system("calc")
    # print("hello")
