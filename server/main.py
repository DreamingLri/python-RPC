import RPCServer
import argparse

def add(a, b):
    return a + b

def sub(a, b):
    return a - b

def parse_args(args):
    parser = argparse.ArgumentParser(description='RPC Client Starter')
    parser.add_argument(
        '-l', '--listen-ip',
        type=str,
        help='Server Listen IP',
        required=True,
        default='127.0.0.1'
        )
    
    parser.add_argument(
        '-p', '--listen-port',
        type=int,
        help='Server Listen Port',
        required=True
        )
    
    return parser.parse_args(args)

if __name__ == '__main__':
    server = RPCServer()
    server.register_function('add', add)
    server.register_function('sub', sub)