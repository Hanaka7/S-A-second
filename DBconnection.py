import socket
import json
from multiprocessing import Process
import re

class DBconnection:
    def __init__(self,addr,recvqueue,sendqueue):
        self.addr = addr
        self.recvqueue = recvqueue
        self.sendqueue = sendqueue
        self.socket = socket.socket()

    def conn(self):
        try:
            self.socket.connect(self.addr)
        except Exception as e:
            print(e)
            self.recv_queue.put('连接失败\n')
            return False
        self.recvqueue.put('连接成功\n')
        print('succeed')
        return True

    def start(self):
        self.start_recv()
        self.start_send()

    def _recv(self):
        try:

            while True:
                data = self.socket.recv(1024).decode()
                data = json.loads(data)
                print(data)
                if data['code'] == 1:
                    self.recvqueue.put(data['msg'] + '\n')
                else:
                    result = data['result']
                    for date, res in result.items():
                        msg = '----------\n' + date + ':\n'
                        for field, value in res.items():
                            msg += field + ': ' + str(value) + '\n'
                            self.recvqueue.put(msg)

        except socket.error:
            self.recvqueue.put('socket close.')
            return
        except Exception as e:
            print(e)
            return

    def start_recv(self):
        t = Process(target=self._recv)
        t.daemon = True
        t.start()

    def _send(self):
        try:

            while True:
                msg = self.sendqueue.get()
                date = re.findall(r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})', msg['date'])
                field = re.split(r'[\s:;]+', msg['field'])[:-1]
                msg = {'date': date, 'field': field}
                msg = json.dumps(msg)
                print(msg)
                self.socket.sendall(msg.encode('UTF-8'))

        except socket.error:
            return
        except Exception as e:
            print(e)
            return

    def start_send(self):
        t = Process(target=self._send)
        t.daemon = True
        t.start()

    def close(self):
        try:
            self.socket.close()
            self.socket = None
        except Exception as e:
            print(e)