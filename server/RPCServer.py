import json
import socket
import ipaddress

class RPCServer:
    def __init__(self):
        self.function_list = {}

    def register_function(self, name, func):
        self.function_list[name] = func




    
