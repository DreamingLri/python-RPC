import socket

class RegistrarCenter:
    def __init__(self):
        self.function_list = {}

    def run_registrar(self, ip, port):
        print('Starting registrar...')
        socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if __name__ == '__main__':
    registrar = RegistrarCenter()