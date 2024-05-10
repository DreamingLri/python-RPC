import RPCServer

def add(a, b):
    return a + b

def sub(a, b):
    return a - b

if __name__ == '__main__':
    server = RPCServer()
    server.register_function('add', add)
    server.register_function('sub', sub)