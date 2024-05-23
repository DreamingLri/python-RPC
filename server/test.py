import socket
import json
import argparse
from socket import *

def add(a, b):
    return a + b

def sub(a, b):
    return a - b

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
    def __init__(self):
        self.function_list = {}

    def register_function(self, name, func):
        self.function_list[name] = func
        registerSocket = socket(AF_INET, SOCK_STREAM)
        registerSocket.connect(('127.0.0.1', 8080))
        data = {
            'function': 'register',
            'name': name
        }
        registerSocket.sendall(json.dumps(data).encode())
        result = registerSocket.recv(1024).decode()
        print(result)
    
    def run_server(self, ip, port):
        print('Starting server...')
        ServerSocket = socket(AF_INET, SOCK_STREAM)
        ServerSocket.bind((ip, port))
        ServerSocket.listen(1024)
        # ServerSocket.setblocking(False)
        print(f'Server started on {ip}:{port}')
        
        while True:
            try:
                connection, address = ServerSocket.accept()
                print(f'Connection from {address}')
                self.handle_rpc(connection)
            except BlockingIOError:
                pass
        

    def handle_rpc(self, connection):
        data = connection.recv(1024)
        data = json.loads(data.decode())
        print(data)
        func_name = data['function']
        args = data['args']
        if func_name 
        result = self.function_list[func_name](*args)
        connection.sendall(str(result).encode())
        connection.close()
        print(f'Connection closed')

if __name__ == '__main__':
    args = parse_args()
    ip = args.listen_ip
    port = args.listen_port


    server = RPCServer()
    server.register_function('add', add)
    server.register_function('sub', sub) 
    server.run_server(ip, port)
    