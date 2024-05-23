import socket
from socket import *
import json
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='RPC Client Starter')
    parser.add_argument(
        '-i', '--ip',
        type=str,
        help='Server IP',
        required=True,
        default='127.0.0.1'
        )
    
    parser.add_argument(
        '-p', '--port',
        type=int,
        help='Server Port',
        required=True
        )
    
    return parser.parse_args()

class RPCClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def call(self, function, *args):
        try:
            ClientSocket = socket(AF_INET, SOCK_STREAM)
            ClientSocket.connect((self.host, self.port))
            ClientSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            ClientSocket.settimeout(5)
            print("Connected to server at {}:{}".format(self.host, self.port))
            data = {
                'function': function,
                'args': args
            }
            ClientSocket.sendall(json.dumps(data).encode())
            result = ClientSocket.recv(1024).decode()
            if result == 'Function not found':
                print('Function {} not found'.format(function))
            else:    
                print('function: {}, args: {}, result: {}'.format(function, args, result))
        except timeout as e:
            print("Connection timeout")
            ClientSocket.close()
        
    
    def list_functions(self):
        ClientSocket = socket(AF_INET, SOCK_STREAM)
        ClientSocket.connect(('127.0.0.1', 8080))
        data = {
            'function': 'list'
        }
        ClientSocket.send(json.dumps(data).encode())
        result = ClientSocket.recv(1024)
        result = json.loads(result.decode())
        print('Available functions: {}'.format(result))
        ClientSocket.close()

    def list_online_servers(self):
        ClientSocket = socket(AF_INET, SOCK_STREAM)
        ClientSocket.connect(('127.0.0.1', 8080))
        data = {
            'function': 'list_online_servers'
        }
        ClientSocket.send(json.dumps(data).encode())
        result = ClientSocket.recv(1024)
        result = json.loads(result.decode())
        print('Online servers: {}'.format(result))
        ClientSocket.close()

    
if __name__ == "__main__":
    args = parse_args()
    host = args.ip
    port = args.port
    client = RPCClient(host, port)

    # while True:
    #     print("hello, here is the RPC client")
    #     print("Connected to server at {}:{}".format(host, port))
    #     print("Here are the available functions:")
    #     print(client.list_functions())
    #     print("Please input the function you want to call:")
    #     function = input()
    #     print("Please input the arguments:")
    #     args = input().split()
    #     print(client.call(function, args))
    client.list_functions()
    client.list_online_servers()
    client.call('add', 1, 2)
    client.call('sub', 3, 2)
        
    






