import ipaddress
import select
import socket
import json
import argparse
from socket import *
from threading import Timer


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
    
    return parser.parse_args()

class RPCServer:
    def __init__(self, ip, port):
        self.function_list = {}
        self.name = 'RPC Server'
        self.ip = ip
        self.port = port

    def register_function(self, name, func):
        self.function_list[name] = func
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
        registerSocket.sendall(json.dumps(data).encode())
        result = registerSocket.recv(1024).decode()
        print(result)
        registerSocket.close()
    
    def run_server(self):
        print('Starting server...')
        
        t = RepeatingTimer(5, server.heartbeat)
        t.start()

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
        
        data = json.loads(data.decode())
        # print(data)

        func_name = data['function']
        args = data['args']
        if self.function_list.get(func_name) is None:
            connection.sendall('Function not found'.encode())
            connection.close()
            print(f'Connection closed')
        else:
            try:
                result = self.function_list[func_name](*args)
            except Exception as e:
                result = f'Error: {str(e)}'
            
            connection.sendall(str(result).encode())
            connection.close()
            print(f'Connection closed')

    def heartbeat(self):
        ip = '127.0.0.1'
        port = 8080
        heartbeatSocket = socket(AF_INET, SOCK_STREAM)
        try:
            heartbeatSocket.connect((ip, port))
        except ConnectionError as e:
            print('Cannot connect to registrar')
            heartbeatSocket.close()
            return ConnectionError
        heartbeatSocket.settimeout(5)
        data = {
            'function': 'heartbeat',
            'name': self.name,
            'ip': self.ip,
            'port': self.port
        }
        try:
            heartbeatSocket.sendall(json.dumps(data).encode())
            result = heartbeatSocket.recv(1024).decode()
            print(result)
        except timeout:
            print('Heartbeat timeout')
            heartbeatSocket.close()

class RepeatingTimer(Timer):
    def run(self):
        while not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
            self.finished.wait(self.interval)


if __name__ == '__main__':
    args = parse_args()
    ip = args.listen_ip
    port = args.listen_port


    server = RPCServer(ip, port)
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
    