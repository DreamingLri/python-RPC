import json
import socket
import ipaddress
import select

class RPCServer:
    def __init__(self):
        self.function_list = {}

    def register_function(self, name, func):
        self.function_list[name] = func

    def handle_rpc(self, connection):
        data = connection.recv(1024)
        data = json.loads(data.decode())
        if data['function'] in self.function_list:
            result = self.function_list[data['function']](*data['args'])
            connection.send(json.dumps(result).encode())
        else:
            connection.send(b'Function not found')
        

    def run_server(self, ip, port):
        print('Starting server...')
        if ipaddress.ip_address(ip).version == 4:
            socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        socket.bind((ip, port))
        socket.listen()
        epoll = select.epoll()
        epoll.register(socket.fileno(), select.EPOLLIN)
        print(f'Server started on {ip}:{port}')

        socket_list = {}
        address_list = {}

        while True:
            events = epoll.poll()
            for fileno, event in events:
                if fileno == socket.fileno():
                    connection, address = socket.accept()
                    connection.setblocking(False)
                    epoll.register(connection.fileno(), select.EPOLLIN)
                    print(f'Connection from {address}')
                    socket_list[connection.fileno()] = connection
                    address_list[connection.fileno()] = address

                elif event & select.EPOLLIN:
                    connection = socket_list[fileno]
                    address = address_list[fileno]
                    self.handle_rpc(connection)

                elif event & select.EPOLLOUT:
                    epoll.unregister(fileno)
                    connection.close()
                    del socket_list[fileno]
                    del address_list[fileno]
                    print(f'Connection closed from {address}')






    
