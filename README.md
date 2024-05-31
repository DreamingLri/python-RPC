# python-RPC
计算机网络大作业
简易RPC服务实现

---

功能包含
1. 服务注册
2. 服务发现
3. 服务调用
4. 支持并发
5. 服务注册中心
6. 异常捕获及处理

---

代码内容

client/ -> RPC客户端及其建议的控制台UI

server/ -> PRC服务端

registrar/ -> 服务注册中心

---

启动命令

客户端：`python3 RPCClient.py -i 127.0.0.1 -p 8080` 或 `python3 clientTUI.py`

服务端：`python3 RPCServer.py -l 127.0.0.1 -p 8081`

服务注册中心：`python3 registrar`

---

如果你发现了任何bug，欢迎提交issue或[发邮件](mailto:dreaminglri@outlook.com)
