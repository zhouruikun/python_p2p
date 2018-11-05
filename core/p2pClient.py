from socketserver import (ThreadingTCPServer, StreamRequestHandler)  # 可以通过as起别名

import threading
import socket
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal
from client_ui import Ui_Client
import time

class P2pClientUiThread(QWidget, Ui_Client):
    connect_signal = pyqtSignal()

    def __init__(self):
        super(P2pClientUiThread, self).__init__()
        self.setWindowIcon(QIcon('../src/img/ico.png'))
        self.setupUi(self)
        self.lineEdit_ip.text()
        self.connect_signal.connect(P2pClientSocketThread.connect_to_server)
        self.pushButton_online.clicked.connect(self.connect_to_server)
        self.pushButton_offline.clicked.connect(self.disconnect_to_server)
        self.pushButton_conn.clicked.connect(self.connect_to_dest_client)
        self.pushButton_offline.setEnabled(False)


class RequestHandlerClient(StreamRequestHandler):
    def handle(self):
        print('get p2p connect')
        while True:
            try:
                row_data = self.rfile.readline().decode("UTF-8")
                if not row_data:
                    break
                rec_data = eval(row_data)
                print(rec_data)
            except Exception as error:
                print(error)


class P2pClientSocketThread(P2pClientUiThread):
    client_status = False
    client_socket = 0
    client_socket_p2p = 0
    client_socket_listen = 0
    client_socket_thread_handle = []
    client_listen_thread_handle = []
    client_socket_thread_flag = False

    def connect_to_server(self):
        # 获取本机计算机名称
        hostname = socket.gethostname()
        # 获取本机ip
        ip = socket.gethostbyname(hostname)
        if not self.client_status:
            server_address = (self.lineEdit_ip.text(), int(self.lineEdit_port.text()))
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket_p2p = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket_listen = ThreadingTCPServer((ip, int(self.lineEdit_localPort.text())), RequestHandlerClient, bind_and_activate=False)
            # print('wait for connections .......')
            #
            try:
                n_net_timeout = 200
                self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, n_net_timeout)
                self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.client_socket.bind((ip, int(self.lineEdit_localPort.text())))
                self.client_socket_p2p.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, n_net_timeout)
                self.client_socket_p2p.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.client_socket_p2p.bind((ip, int(self.lineEdit_localPort.text())))

                self.client_socket.connect(server_address)
                self.client_socket_listen.allow_reuse_address = True
                self.client_socket_listen.server_bind()
                self.client_socket_listen.server_activate()
                self.client_status = True
                self.pushButton_offline.setEnabled(True)
                self.pushButton_online.setEnabled(False)

                self.client_socket_thread_handle = threading.Thread(target=P2pClientSocketThread.client_socket_thread, args=(self,), name='client_socket_thread_handle')
                self.client_socket_thread_handle.setDaemon(True)
                self.client_socket_thread_handle.start()
            except Exception as error:
                print(error)
                QMessageBox.information(self, "Error", "Connect to server fail.", QMessageBox.Yes)

    def client_listen_thread(self):
        self.client_socket_listen.serve_forever()

    def client_socket_thread(self):
        self.client_socket_thread_flag = True
        while self.client_socket_thread_flag:
            try:
                ack = self.client_socket.recv(1024).decode("UTF-8")
                if ack:
                    rec_data = eval(ack)
                if 'ip' in rec_data:
                    server_address = rec_data['ip']
                    print("get ip " + str(server_address)+" start connect to dest ")
                    try:
                        self.client_socket_p2p.connect(server_address)
                        print('connect to dest success')
                    except Exception as error:
                        print('connect to dest fail')
                if 'query_conn' in rec_data:
                    server_address = rec_data['query_conn']['ip']
                    print("get query_conn  " + str(server_address) + " start listen ")
                    self.client_listen_thread_handle = threading.Thread(
                        target=P2pClientSocketThread.client_listen_thread, args=(self,),
                        name='client_listen_thread_handle')
                    self.client_listen_thread_handle.setDaemon(True)
                    self.client_listen_thread_handle.start()
                    self.client_socket_p2p.connect(server_address)

            except Exception as error:
                 pass

    def disconnect_to_server(self):
        if self.client_status:
            try:
                self.client_socket.close()
                self.client_status = False
                self.pushButton_offline.setEnabled(False)
                self.pushButton_online.setEnabled(True)
                self.client_socket_thread_flag = False
            except Exception as error:
                print(error)

    def connect_to_dest_client(self):
        self.get_dest_ip()

    def get_dest_ip(self):
        dest_uid = self.lineEdit_dest_UID.text()
        message = {'dest': dest_uid}
        if self.client_status:
            self.client_socket.send((str(message)+'\r\n').encode())


def run_client():
    app = QApplication(sys.argv)
    p2p_client_ui_socket_thread = P2pClientSocketThread()
    p2p_client_ui_socket_thread.show()
    sys.exit(app.exec_())
