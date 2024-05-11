import socket
import json
import argparse

class RPCClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def call(self, function, *args):
        socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.connect((self.host, self.port))
        data = {
            'function': function,
            'args': args
        }
        socket.send(json.dumps(data).encode())
        result = socket.recv(1024)
        return json.loads(result.decode())



