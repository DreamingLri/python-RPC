import ipaddress
import select
import socket
import json
import argparse
from socket import *


def add(a, b):
    return a + b

def sub(a, b):
    return a - b

def mul(a, b):
    return a * b

def div(a, b):
    if b != 0:
        return a / b
    else:
        return 'Error: Division by zero'

def mod(a, b):
    if b != 0:
        return a % b
    else:
        return 'Error: Division by zero'
    
def pow(a, b):
    return a ** b

def max(a, b):
    return a if a > b else b

def min(a, b):
    return a if a < b else b

def sqrt(a):
    return a ** 0.5

def is_odd(a):
    return a % 2 != 0

def is_even(a):
    return a % 2 == 0

def parse_args():
    parser = argparse.ArgumentParser(description='RPC Client Starter')
    parser.add_argument(
        '-l', '--listen-ip',
        type=str,
        help='Server Listen IP',
        required=True,
        default='127.0.0.1'
        )
    
    parser.add_argument(
        '-p', '--listen-port',
        type=int,
        help='Server Listen Port',
        required=True
        )
    
    parser.add_argument(
        '-n', '--name',
        type=str,
        help='Server Name',
        default='RPC Server',
        required=False
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

class RPCServer:
    def __init__(self, ip, port, name):
        self.function_list = {}
        self.name = name
        self.ip = ip
        self.port = port

    def register_function(self, name, func):
        #注册函数
        self.function_list[name] = func
        #连接注册中心
        registerSocket = socket(AF_INET, SOCK_STREAM)
        try:
            registerSocket.connect(('127.0.0.1', 8080))
        except ConnectionError as e:
            print('Cannot connect to registrar')
            registerSocket.close()
            return
        data = {
            'function': 'register',
            'name': name
        }
        #发送注册消息
        registerSocket.sendall(format_message(data))
        #接收注册结果
        result = registerSocket.recv(1024)
        result = parse_message(result)
        if result is None:
            print('Cannot parse message')
            registerSocket.close()
        #输出注册结果
        print(result['name'] + ' ' + result['message'])
        registerSocket.close()
    
    def run_server(self):
        print('Starting server...')
        
        self.set_online()

        if ipaddress.ip_address(self.ip).version == 4:
            ServerSocket = socket(AF_INET, SOCK_STREAM)
        else:
            self.ip = '[{}]'.format(self.ip)
            ServerSocket = socket(AF_INET6, SOCK_STREAM)
        
        ServerSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        ServerSocket.bind((self.ip, self.port))
        ServerSocket.listen(1024)
        # ServerSocket.setblocking(False)
        

        epoll = select.epoll()
        epoll.register(ServerSocket.fileno(), select.EPOLLIN)
        
        socket_list = {}
        client_address_list = {}
        print(f'Server started on {self.ip}:{self.port}')
        while True:
            try:
                epoll_list = epoll.poll()
                for sock_fileno, events in epoll_list:
                    if sock_fileno == ServerSocket.fileno():
                        connection, address = ServerSocket.accept()
                        connection.setblocking(False)
                        print(f'Connection from {address}')
                        epoll.register(connection.fileno(), select.EPOLLIN)
                        socket_list[connection.fileno()] = connection
                        client_address_list[connection.fileno()] = address
                    
                    elif events & select.EPOLLIN:
                        connection = socket_list[sock_fileno]
                        self.handle_rpc(connection)
                    
                    elif events & select.EPOLLHUP:
                        epoll.unregister(sock_fileno)
                        socket_list[sock_fileno].close()
                        del socket_list[sock_fileno]
                        del client_address_list[sock_fileno]
            except BlockingIOError:
                pass
        

    def handle_rpc(self, connection):
        connection.settimeout(5)
        try:
            data = connection.recv(1024)
        except timeout:
            print('Request timeout')
            connection.close()
        
        data = parse_message(data)

        if data is None:
            print('Cannot parse message')
            connection.close()
            return
        
        if data['function'] == 'heartbeat':
            result = {
                'function': 'heartbeat',
                'result': 'OK'
            }
            connection.sendall(format_message(result))
            connection.close()
            return
        
        try:
            func_name = data['function']
            args = data['args']
        except KeyError:
            print('Invalid request')
            connection.close()
            return
        
        if self.function_list.get(func_name) is None:
            data = {
                'result': 'Function not found'
            }
            try:
                connection.sendall(format_message(data))
                connection.close()
            except timeout:
                print('Send message timeout')
                connection.close()
            except Exception as e:
                print('Send message error {}'.format(str(e)))
                connection.close()
        else:
            try:
                result = self.function_list[func_name](*args)
            except Exception as e:
                result = f'Error: {str(e)}'
            
            data = {
                'result': result
            }
            try:
                connection.sendall(format_message(data))
                connection.close()
            except timeout:
                print('Send message timeout')
                connection.close()
            except Exception as e:
                print('Send message error {}'.format(str(e)))
                connection.close()

    # 发送上线消息
    def set_online(self):
        ip = '127.0.0.1'
        port = 8080
        onlineSocket = socket(AF_INET, SOCK_STREAM)
        onlineSocket.connect((ip, port))
        onlineSocket.settimeout(5)
        # 上线消息内容
        data = {
            'function': 'online',
            'name': self.name,
            'ip': self.ip,
            'port': self.port
        }
        try:
            # 发送消息
            onlineSocket.sendall(format_message(data))
            # 接收回复
            result = onlineSocket.recv(1024)
            result = parse_message(result)
            # 输出回复
            print(result)
        except timeout:
            print('Connect registrar timeout')
            onlineSocket.close()
        except ConnectionError as e:
            print('Cannot registrar error {}'.format(str(e)))
            onlineSocket.close()


if __name__ == '__main__':
    args = parse_args()
    ip = args.listen_ip
    port = args.listen_port
    name = args.name


    server = RPCServer(ip, port, name)
    server.register_function('add', add)
    server.register_function('sub', sub)
    server.register_function('mul', mul)
    server.register_function('div', div)
    server.register_function('mod', mod)
    server.register_function('pow', pow)
    server.register_function('max', max)
    server.register_function('min', min)
    server.register_function('sqrt', sqrt)
    server.register_function('is_odd', is_odd)
    server.register_function('is_even', is_even)
    server.run_server()
    