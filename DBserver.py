import pymssql
import socket
from multiprocessing.pool import Pool
import json


class DBserver:
    def __init__(self, user, passwd, host, dbname, tablename):
        self.host = host
        self.dbname = dbname
        self.user = user
        self.passwd = passwd
        self.table = tablename
        self.pool = Pool(processes=3)

    def listen(self):
        self.socket = socket.socket()
        self.socket.bind(('localhost', 4396))
        self.socket.listen(10)
        while True:
            oneconn, addr = self.socket.accept()
            print(addr)
            self.pool.apply_async(self.connect, (oneconn,))#使用apply_async 进程异步非阻塞

    def connect(self, oneconn):
        conn, cursor = self.new_cursor()
        while True:
            try:
                msg = oneconn.recv(1024)
                msg = json.loads(msg.decode())
                result = {'code': 0, 'result': {}}
                dateall = msg['date']
                field = msg['field']
                for date in dateall:
                    result['result'][date] = {}
                    sql = self.set_sql(date, field)
                    cursor.execute(sql)
                    receive = cursor.fetchone()
                    for i in range(len(field)):
                        result['result'][date][field[i]] = receive[i]
                result = json.dumps(result)
                oneconn.sendall(result.encode('UTF-8'))  #sendall替换了send
            except TypeError:
                result = {'code': 1, 'msg': '查询内容不存在'}
                result = json.dumps(result).encode('UTF-8')
                oneconn.sendall(result)
            except Exception as e:
                print(e)
                cursor.close()
                oneconn.close()
                self.close()
                return

    def set_sql(self, date, args):
        field = ''
        for i in args:
            field += i
            field += ','
        field = field[:-1]
        sql = 'select {} from {} where 日期 = \'{}\''.format(field, self.table, date)#格式化字符串输入可供查询的sql语句
        print(sql)
        return sql

    def new_cursor(self):
        try:
            conn = pymssql.connect(host=self.host, user=self.user, password=self.passwd,
                                 database=self.dbname, charset='utf8')
            cursor = conn.cursor()
            return conn, cursor
        except Exception as e:
            raise e



    def close(self):
        try:
            self.socket.close()
        except:
            return

    def __getstate__(self):
        self_dict = self.__dict__.copy()
        del self_dict['pool']
        return self_dict

    def __setstate__(self, state):
        self.__dict__.update(state)


if __name__ == '__main__':
    host = 'localhost'
    port = 2345
    user = 'test'
    passwd = '123456'
    dbname = 'companydata'
    tablename = 'data'

    print('服务启动')

    server = DBserver(user, passwd, host, dbname, tablename)
    server.listen()

