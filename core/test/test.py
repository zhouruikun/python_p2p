import socket
tcp1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#在绑定前调用setsockopt让套接字允许地址重用
tcp1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

tcp2.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, 1)
#接下来两个套接字都也可以绑定到同一个端口上
# tcp1.bind(('', 12345))
tcp2.bind(('', 3333))
# tcp2.connect(('106.14.226.150', 1234))
tcp2.connect(('192.168.0.106', 1234))
tcp2.close()