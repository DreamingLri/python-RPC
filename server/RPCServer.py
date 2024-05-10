import json
import socket
import ipaddress
import select

class RPCServer:
    def __init__(self):
        self.function_list = {}

    def register_function(self, name, func):
        self.function_list[name] = func

    def run_server(self, ip, port):
        print('Starting server...')
        if ipaddress.ip_address(ip).version == 4:
            socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket.bind((ip, port))
            socket.listen()
            epoll = select.epoll()
            epoll.register(socket.fileno(), select.EPOLLIN)
            print(f'Server started on {ip}:{port}')

            

            while True:
                events = epoll.poll()
                for fileno, event in events:
                    if fileno == socket.fileno():
                        connection, address = socket.accept()
                        connection.setblocking(False)
                        epoll.register(connection.fileno(), select.EPOLLIN)
                        print(f'Connection from {address}')


                    elif event & select.EPOLLIN:
                        pass
                    elif event & select.EPOLLOUT:
                        epoll.unregister(fileno)
                        epoll.close()
                        connection.close()
                        print('Connection closed')




    
