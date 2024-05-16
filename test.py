import json

message = '{"function": "register", "name": "add"}'

function_list = []

message = json.loads(message)
if message['function'] == 'register':
    function_list.append(message['name'])
    print('Registered')
print(function_list[0])
