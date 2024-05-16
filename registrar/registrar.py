import socket
from socket import *
import json

class RegisterCenter:
    def __init__(self):
        self.function_list = [
        ]

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
            print(f'Connection from {address}')
            connection.close()
            print(f'Connection closed')
            

    def list_functions(self):
        return self.function_list
    
    def register_function(self, name):
        self.function_list.append(name)
    
    def function_service(self, connection):
        data = connection.recv(1024)
        data = json.loads(data.decode())
        if data['function'] == 'register':
            self.register_function(data['name'])
            connection.send(b'Registered')
            print(self.function_list)
        elif data['function'] == 'list':
            connection.send(json.dumps(self.list_functions()).encode())
        else:
            connection.send(b'Function not found')
                
        

        

    def heartbeat(self):
        pass


if __name__ == '__main__':
    register = RegisterCenter()
    register.run_register('127.0.0.1', 8080)
