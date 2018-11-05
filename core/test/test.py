#导入该模块
import socketserver

#定义一个类，继承socketserver.BaseRequestHandler
class Server(socketserver.BaseRequestHandler):
    def handle(self):
    #打印客户端地址和端口
        print('New connection:',self.client_address)
    #循环
        while True:
        #接收客户发送的数据
            data = self.request.recv(1024)
            if not data:break#如果接收数据为空就跳出，否则打印
            print('Client data:',data.decode())
            self.request.send(data)#将收到的信息再发送给客户端

if __name__ == '__main__':
    host,port = ('',3333)  #定义服务器地址和端口
    server = socketserver.ThreadingTCPServer((host,port),Server) #实现了多线程的socket通话
    server.serve_forever()#不会出现在一个客户端结束后，当前服务器端就会关闭或者报错，而是继续运行，与其他的客户端继续进行通话。