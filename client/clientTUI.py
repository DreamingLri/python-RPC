import RPCCLient

client = None
server_joined = False

while True:
    print('====================================')
    print('Hello, welcome to the RPC client!')
    if server_joined:
        print('Server joined:', client.ip, client.port)
    print('====================================')
    print('1. Join server')
    print('2. Call function')
    print('3. Exit')
    choice = input('Please select an option: ')
    match choice:
        case '1':
            print('Please input the registrar IP and port')
            ip = input('IP: ')
            port = input('Port: ')
            port = int(port)
            client = RPCCLient.RPCClient(ip, port)
            server_list = client.list_online_servers()
            print('Online servers:', server_list)
            client.join_server()
            server_joined = True
        case '2':
            if not server_joined:
                print('Please join a server first!')
                continue
            function_list = client.list_functions()
            function = input('Please input the function name: ')
            args = input('Please input the arguments(split by ,): ')
            args = args.split(',')
            args = [eval(arg) for arg in args]
            print(args)
            client.call(function, *args)
        case '3':
            break