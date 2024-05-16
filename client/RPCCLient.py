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
        ClientSocket = socket(AF_INET, SOCK_STREAM)
        ClientSocket.connect((self.host, self.port))
        data = {
            'function': function,
            'args': args
        }
        ClientSocket.send(json.dumps(data).encode())
        result = ClientSocket.recv(1024)
        return json.loads(result.decode())
    
    def list_functions(self):
        ClientSocket = socket(AF_INET, SOCK_STREAM)
        ClientSocket.connect(('127.0.0.1', 8080))
        data = {
            'function': 'list'
        }
        ClientSocket.send(json.dumps(data).encode())
        result = ClientSocket.recv(1024)
        return json.loads(result.decode())
    
if __name__ == "__main__":
    args = parse_args()
    host = args.ip
    port = args.port
    client = RPCClient(host, port)

    print("hello, here is the RPC client")
    print("Connected to server at {}:{}".format(host, port))
    print("Here are the available functions:")
    print(client.list_functions())
        
    






