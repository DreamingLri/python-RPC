import socket
from socket import *
import json
import argparse
import ipaddress

def parse_args():
    parser = argparse.ArgumentParser(description='RPC Client Starter')
    parser.add_argument(
        '-i', '--reg_ip',
        type=str,
        help='Registrar Server IP',
        required= True,
        default='127.0.0.1'
        )
    
    parser.add_argument(
        '-p', '--reg_port',
        type=int,
        help='Registrar Server Port',
        required= True,
        default= 8080
        )
    
    return parser.parse_args()

# 解决粘包问题
def format_message(data):
    data = json.dumps(data).encode()
    return len(data).to_bytes(4, byteorder='big') + data

def parse_message(data):
    message_length = int.from_bytes(data[:4], byteorder='big')
    if len(data) < 4 + message_length:
        return None
    return json.loads(data[4:4 + message_length].decode())

class RPCClient:
    def __init__(self, ip, port):
        self.reg_ip = ip
        self.reg_port = port
        self.ip = None
        self.port = None

    def call(self, function, *args):
        try:
            if self.ip == None or self.port == None:
                print('You are not connect to any server, please use func join_server() first!')
                return
            
            if ipaddress.ip_address(self.ip).version == 6:
                ip_address = ipaddress.IPv6Address(self.ip).compressed
                ClientSocket = socket(AF_INET6, SOCK_STREAM)
                ClientSocket.connect((ip_address, self.port))
            else:
                ClientSocket = socket(AF_INET, SOCK_STREAM)
                ClientSocket.connect((self.ip, self.port))

            ClientSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            ClientSocket.settimeout(5)
            print("Connected to server at {}:{}".format(self.ip, self.port))
            data = {
                'function': function,
                'args': args
            }
            ClientSocket.sendall(format_message(data))
            result = ClientSocket.recv(1024)
            result = parse_message(result)

            if result['result'] == 'Function not found':
                print('Function {} not found'.format(function))
            else:    
                print('function: {}, args: {}, result: {}'.format(function, args, result['result']))

        except timeout as e:
            print("Connection timeout")
            ClientSocket.close()

        except ConnectionError as e:
            print("Cannot connect to server {}:{}".format(self.ip, self.port))
            ClientSocket.close()
        
    
    def list_functions(self):
        if ipaddress.ip_address(self.reg_ip).version == 6:
            ip_address = ipaddress.IPv6Address(self.ip).compressed
            ClientSocket = socket(AF_INET6, SOCK_STREAM)
            ClientSocket.connect((ip_address, self.reg_port))
        else:
            ClientSocket = socket(AF_INET, SOCK_STREAM)
            ClientSocket.connect((self.reg_ip, self.reg_port))

        data = {
            'function': 'list'
        }

        ClientSocket.send(format_message(data))
        result = ClientSocket.recv(1024)
        result = parse_message(result)
        print('Available functions: {}'.format(result))
        ClientSocket.close()

    def list_online_servers(self):
        if ipaddress.ip_address(self.reg_ip).version == 6:
            ip_address = ipaddress.IPv6Address(self.reg_ip).compressed
            ClientSocket = socket(AF_INET6, SOCK_STREAM)
            ClientSocket.connect((ip_address, self.reg_port))
        else:
            ClientSocket = socket(AF_INET, SOCK_STREAM)
            ClientSocket.connect((self.reg_ip, self.reg_port))

        data = {
            'function': 'list_online_servers'
        }

        ClientSocket.send(format_message(data))
        result = ClientSocket.recv(1024)
        result = parse_message(result)
        print('Online servers: {}'.format(result))
        ClientSocket.close()

    def join_server(self):
        if ipaddress.ip_address(self.reg_ip).version == 6:
            ip_address = ipaddress.IPv6Address(self.reg_ip).compressed
            ClientSocket = socket(AF_INET6, SOCK_STREAM)
            ClientSocket.connect((ip_address, self.reg_port))
        else:
            ClientSocket = socket(AF_INET, SOCK_STREAM)
            ClientSocket.connect((self.reg_ip, self.reg_port))

        data = {
            'function': 'join_server'
        }
        ClientSocket.send(format_message(data))
        result = ClientSocket.recv(1024)
        result = parse_message(result)
        if result == 'No server to connect':
            print('There are no servers to connect!')
            ClientSocket.close()
            return
        
        self.ip = result[1]
        self.port = result[2]



    
if __name__ == "__main__":
    args = parse_args()
    reg_ip = args.reg_ip
    reg_port = args.reg_port
    client = RPCClient(reg_ip, reg_port)

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
    client.join_server()
    client.call('add', 1, 2)
    client.call('sub', 3, 2)
        
    






