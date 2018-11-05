from socketserver import (ThreadingTCPServer, StreamRequestHandler as SRH)  # 可以通过as起别名
from time import ctime
import uuid
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHeaderView, QTableWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal

from server_ui import Ui_Server
import threading
HOST = ''
PORT = 1234
Address = (HOST, PORT)
ConnectionList = {}
client_socket = {}
p2p_server_ui_thread = []
ConnectionCount = 0


class P2pServerUiThread(QWidget, Ui_Server):
    NewConnectionSignal = pyqtSignal(int)

    def __init__(self):
        super(P2pServerUiThread, self).__init__()
        self.setWindowIcon(QIcon('../src/img/ico.png'))
        self.setupUi(self)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.setColumnCount(4)
        self.NewConnectionSignal.connect(self.refresh_lcd)

    def refresh_lcd(self, size):
        self.lcdNumber.display(size)
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        for item in ConnectionList.values():
            row_count = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_count)
            self.tableWidget.setItem(row_count, 0, QTableWidgetItem(str(item['ip'])))
            self.tableWidget.setItem(row_count, 1, QTableWidgetItem(str(item['UID'])))
            self.tableWidget.setItem(row_count, 2, QTableWidgetItem(str(item['Status'])))
            self.tableWidget.setItem(row_count, 3, QTableWidgetItem(str(item['Conn'])))


class P2pServerSocketThread:
    @staticmethod
    def run_server_socket():
        tcp_server = ThreadingTCPServer(Address, MyRequestHandler, bind_and_activate=False)
        # tcp_server.allow_reuse_address = True
        tcp_server.server_bind()
        tcp_server.server_activate()
        print('wait for connections .......')
        tcp_server.serve_forever()


class MyRequestHandler(SRH):
    UID = []

    def finish(self):
        global p2p_server_ui_thread, ConnectionCount, ConnectionList
        ConnectionCount = ConnectionCount - 1
        p2p_server_ui_thread.NewConnectionSignal.emit(ConnectionCount)
        ConnectionList.pop(self.UID)
        client_socket.pop(self.UID)

    def handle(self):
        global p2p_server_ui_thread, ConnectionCount, ConnectionList
        self.UID = str(uuid.uuid1())
        print('已经连接:', self.client_address)
        ConnectionCount = ConnectionCount+1
        p2p_server_ui_thread.NewConnectionSignal.emit(ConnectionCount)
        ConnectionList[self.UID] = {'ip': self.client_address, 'UID': self.UID, 'Status': '0', 'Conn': '0'}
        client_socket[self.UID] = self.request
        while True:
            try:
                row_data = self.rfile.readline().decode("UTF-8")
                if not row_data:
                    break
                rec_data = eval(row_data)

                print(rec_data)
                if 'dest' in rec_data:
                    if rec_data['dest'] in ConnectionList:
                        ack_get_ip_pack = str(ConnectionList[rec_data['dest']])
                        self.wfile.write(ack_get_ip_pack.encode("UTF-8"))
                        notify_dest_pack = {}
                        notify_dest_pack['query_conn'] = ConnectionList[self.UID]
                        client_socket[rec_data['dest']].sendall(str(notify_dest_pack).encode())
                    else:
                        self.wfile.write(('[%s] %s' % (ctime(), "No Client\r\n")).encode("UTF-8"))
                else:
                    self.wfile.write(('[%s] %s' % (ctime(), "Format Error\r\n")).encode("UTF-8"))
            except Exception as error:
                print(error)
                self.wfile.write(('[%s] %s' % (ctime(), "Format Error\r\n")).encode("UTF-8"))


def run_server():
    app = QApplication(sys.argv)
    global p2p_server_ui_thread
    p2p_server_ui_thread = P2pServerUiThread()
    p2p_server_ui_thread.show()
    p2p_server_socket_thread = P2pServerSocketThread()
    run_server_socket_thread = threading.Thread(target=p2p_server_socket_thread.run_server_socket)
    run_server_socket_thread.setDaemon(True)
    run_server_socket_thread.start()
    sys.exit(app.exec_())


