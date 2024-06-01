import socket
from socket import *
import json
import threading
import time
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='RPC registrar Server Starter')
    parser.add_argument(
        '-i', '--ip',
        type=str,
        help='Registrar Server IP',
        required= False,
        default='127.0.0.1'
        )
    
    parser.add_argument(
        '-p', '--port',
        type=int,
        help='Registrar Server Port',
        required= False,
        default= 8080
        )
    
    return parser.parse_args()

# 解决粘包问题
def format_message(data):
    data = json.dumps(data).encode()
    return len(data).to_bytes(4, byteorder='big') + data

def parse_message(data):
    message_length = int.from_bytes(data[:4], byteorder='big')
    if len(data) < 4 + message_length:
        return None
    return json.loads(data[4:4 + message_length].decode())

class RegisterCenter:
    def __init__(self):
        self.function_list = []
        self.server_list = []
        self.counter = 0

    def run_register(self, ip, port):
        print('Starting registrar...')
        RegisterSocket = socket(AF_INET, SOCK_STREAM)
        RegisterSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        RegisterSocket.bind((ip, port))
        RegisterSocket.listen()
        print(f'Registrar started on {ip}:{port}')
        while True:
            connection, address = RegisterSocket.accept()
            self.function_service(connection)

    def heartbeat(self, server):
        # 每隔5秒进行一次心跳检测
        while True:
            time.sleep(5)
            # 如果服务器不在服务器列表中，则退出
            if server not in self.server_list:
                break
            try:
                # 向服务器发送心跳包
                heartbeatSocket = socket(AF_INET, SOCK_STREAM)
                heartbeatSocket.connect((server[1], server[2]))
                data = {
                    'function': 'heartbeat'
                }
                heartbeatSocket.sendall(format_message(data))
                # 接收服务器返回的心跳包
                result = heartbeatSocket.recv(1024)
                result = parse_message(result)
                if result is None:
                    print('Cannot parse message')
                    heartbeatSocket.close()
                heartbeatSocket.close()
            # 如果服务器连接失败，则输出服务器下线信息，并将服务器从服务器列表中删除
            except ConnectionError as e:
                print(f'Server {server[0]} is offline')
                self.server_list.remove(server)
                break
                

    def list_functions(self):
        return self.function_list
    
    def register_function(self, name):
        self.function_list.append(name)

    def delete_function(self, name):
        self.function_list.remove(name)
    
    def function_service(self, connection):
        connection.settimeout(5)
        try:
            data = connection.recv(1024)
        except timeout:
            print('Connection timeout')
            connection.close()
        
        data = parse_message(data)
        # 对函数进行判断，如果函数不存在则注册，否则返回函数已存在
        if data['function'] == 'register':
            # 未出现过的函数则注册
            if data['name'] not in self.function_list:
                self.register_function(data['name'])
                data = {
                    'message': 'Registered',
                    'name': data['name']
                }
                connection.sendall(format_message(data))
                print(f'Function {data["name"]} registered')
            # 已存在的函数则返回函数已存在
            else:
                data = {
                    'message': 'Function already exists',
                    'name': data['name']
                }
                connection.sendall(format_message(data))

        elif data['function'] == 'list':
            # 进行消息序列化
            data = format_message(self.list_functions())
            connection.sendall(data)

        elif data['function'] == 'delete':
            self.delete_function(data['name'])
            data = {
                'message': 'Deleted',
                'name': data['name']
            }
            connection.sendall(format_message(data))

        elif data['function'] == 'online':
            # 未出现过的服务器则注册
            if (data['name'], data['ip'], data['port']) not in self.server_list:
                # 将服务器信息加入服务器列表
                self.server_list.append((data['name'], data['ip'], data['port']))
                # 输出服务器上线信息
                print(f'Server {data["name"]} is online')
                # 返回服务器已在线
                connection.sendall(format_message('Server {} is online'.format(data['name'])))
                # 创建线程进行心跳检测
                thread = threading.Thread(target=self.heartbeat, args=((data['name'], data['ip'], data['port']),))
                thread.start()
            # 已存在的服务器则返回服务器已在线
            else:
                connection.sendall(format_message('Server already online'))

        elif data['function'] == 'list_online_servers':
            data = format_message(self.server_list)
            connection.sendall(data)

        elif data['function'] == 'join_server':
            if len(self.server_list) == 0:
                connection.sendall(format_message('No server to connect'))
            else:
                # 轮询算法
                if self.counter >= len(self.server_list):
                    self.counter = 0
                server = self.server_list[self.counter]
                self.counter = (self.counter + 1) % len(self.server_list)
                connection.sendall(format_message(server))             

        else:
            connection.sendall(format_message('Function not found'))

            

if __name__ == '__main__':
    args = parse_args()
    ip = args.ip
    port = args.port
    register = RegisterCenter()
    register.run_register(ip, port)
