import socket
from socket import *
import json
import threading
import time

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
        while True:
            time.sleep(5)
            if server not in self.server_list:
                break
            try:
                heartbeatSocket = socket(AF_INET, SOCK_STREAM)
                heartbeatSocket.connect((server[1], server[2]))
                data = {
                    'function': 'heartbeat'
                }
                heartbeatSocket.sendall(format_message(data))
                result = heartbeatSocket.recv(1024)
                result = parse_message(result)
                if result is None:
                    print('Cannot parse message')
                    heartbeatSocket.close()
                # print(result)
                heartbeatSocket.close()
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
        if data['function'] == 'register':
            if data['name'] not in self.function_list:
                self.register_function(data['name'])
                data = {
                    'message': 'Registered',
                    'name': data['name']
                }
                connection.sendall(format_message(data))
                print(f'Function {data["name"]} registered')
            else:
                data = {
                    'message': 'Function already exists',
                    'name': data['name']
                }
                connection.sendall(format_message(data))

        elif data['function'] == 'list':
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
            connection.sendall(format_message('Receive heartbeat from registrar'))
            if (data['name'], data['ip'], data['port']) not in self.server_list:
                self.server_list.append((data['name'], data['ip'], data['port']))
                print(f'Server {data["name"]} is online')
                thread = threading.Thread(target=self.heartbeat, args=((data['name'], data['ip'], data['port']),))
                thread.start()

        elif data['function'] == 'list_online_servers':
            data = format_message(self.server_list)
            connection.sendall(data)

        elif data['function'] == 'join_server':
            if len(self.server_list) == 0:
                connection.sendall(format_message('No server to connect'))
            else:
                # 轮询算法
                server = self.server_list[self.counter]
                self.counter = (self.counter + 1) % len(self.server_list)
                connection.sendall(format_message(server))             

        else:
            connection.sendall(format_message('Function not found'))

            

if __name__ == '__main__':
    register = RegisterCenter()
    register.run_register('127.0.0.1', 8080)
