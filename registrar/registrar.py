import socket
from socket import *
import json
import time


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
                

    def list_functions(self):
        return self.function_list
    
    def register_function(self, name):
        self.function_list.append(name)

    def delete_function(self, name):
        self.function_list.remove(name)
    
    def function_service(self, connection):
        connection.settimeout(5)
        try:
            data = connection.recv(1024).decode()
        except timeout:
            print('Connection timeout')
            connection.close()
        
        data = json.loads(data)
        if data['function'] == 'register':
            if data['name'] not in self.function_list:
                self.register_function(data['name'])
                connection.sendall(b'Registered')
                print(f'Function {data["name"]} registered')
            else:
                connection.sendall(b'Function already exists')

        elif data['function'] == 'list':
            connection.sendall(json.dumps(self.list_functions()).encode())

        elif data['function'] == 'delete':
            self.delete_function(data['name'])
            connection.sendall(b'Deleted')

        elif data['function'] == 'heartbeat':
            connection.send(b'Receive heartbeat from registrar')
            if (data['name'], data['ip'], data['port']) not in self.server_list:
                self.server_list.append((data['name'], data['ip'], data['port']))
                print(f'Server {data["name"]} is online')

        elif data['function'] == 'list_online_servers':
            connection.sendall(json.dumps(self.server_list).encode())

        elif data['function'] == 'join_server':
            if len(self.server_list) == 0:
                connection.sendall(json.dumps('No server to connect').encode())
            else:
                # 轮询算法
                server = self.server_list[self.counter]
                self.counter = (self.counter + 1) % len(self.server_list)
                connection.sendall(json.dumps(server).encode())             

        else:
            connection.sendall(b'Function not found')

            

if __name__ == '__main__':
    register = RegisterCenter()
    register.run_register('127.0.0.1', 8080)
