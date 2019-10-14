import DBconnection
from PLclient import PLclient

from multiprocessing import Queue

if __name__ == '__main__':
    send = Queue()
    recv = Queue()

    conn = DBconnection.DBconnection(('localhost', 4396), recv, send)

    if not conn.conn():
        exit(1)
    conn.start()
    client = PLclient(('localhost', 4396), recv, send)
    conn.close()
