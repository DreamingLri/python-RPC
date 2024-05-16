import socket
import json

class RegisterCenter:
    def __init__(self):
        self.function_list = {}

    def run_register(self, ip, port):

        print('Starting registrar...')
        socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.bind((ip, port))
        socket.listen()
        print(f'Registrar started on {ip}:{port}')
        while True:
            connection, address = socket.accept()
            self.function_service(connection)
            

    def list_functions(self):
        return self.function_list
    
    def register_function(self, name):
        self.function_list.append(name)
    
    def function_service(self, connection):
        while True:
            data = connection.recv(1024)
            data = json.loads(data.decode())
            if data['function'] == 'register':
                self.register_function(data['name'])
                connection.send(b'Registered')
            elif data['function'] == 'list':
                connection.send(json.dumps(self.list_functions()).encode())
            else:
                connection.send(b'Function not found')
        

    def heartbeat(self):
        pass


if __name__ == '__main__':
    register = RegisterCenter()
    register.run_register('127.0.0.1', 8080)
