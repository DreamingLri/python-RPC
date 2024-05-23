import socket
from socket import *
import json
import signal

class RegisterCenter:
    def __init__(self):
        self.function_list = []
        self.server_list = []

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
            # print(f'Connection from {address}')
            # connection.close()
            # print(f'Connection closed')
                

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
                connection.send(b'Registered')
                print(f'Function {data["name"]} registered')
            else:
                connection.send(b'Function already exists')

        elif data['function'] == 'list':
            connection.send(json.dumps(self.list_functions()).encode())

        elif data['function'] == 'delete':
            self.delete_function(data['name'])
            connection.send(b'Deleted')

        elif data['function'] == 'heartbeat':
            connection.send(b'Receive heartbeat from registrar')
            if self.server_list.count(data['name']) == 0:
                self.server_list.append(data['name'])
                print(f'Server {data["name"]} is online')

        elif data['function'] == 'list_online_servers':
            connection.send(json.dumps(self.server_list).encode())

        else:
            connection.send(b'Function not found')

                
        

if __name__ == '__main__':
    register = RegisterCenter()
    register.run_register('127.0.0.1', 8080)
