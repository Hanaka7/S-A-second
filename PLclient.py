import tkinter as tk
from threading import Thread

class PLclient:
    def __init__(self, addr, recv_queue, send_queue):
        self.addr = addr
        self.recv_queue = recv_queue
        self.send_queue = send_queue
        self._init()
        self._on_recv()
        self.window.mainloop()

    def _init(self):
        self.window =tk.Tk()
        self.window.resizable(width=False, height=False)
        self.window.title("查询")
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

        frame_left = tk.Frame(self.window, width=500, height=500, bg='white')
        frame_right = tk.Frame(self.window, width=300, height=500, bg='white')

        self.msgBox=tk.Text(frame_left)
        self.dateBox=tk.Text(frame_right)
        self.fieldBox=tk.Text(frame_right)
        self.dataLabel=tk.Label(frame_right,text="查询日期")
        self.fieldLabel=tk.Label(frame_right,text='查询条目')
        self.sendButton=tk.Button(frame_right,text="查询",command=self._on_send)

        frame_left.grid(row=0, column=0, padx=2, pady=5)
        frame_right.grid(row=0, column=1, padx=2, pady=5)

        self.msgBox.place(x=0, width=480, height=500)
        self.fieldLabel.place(x=20, y=200, width=80, height=20)
        self.dataLabel.place(x=20, y=300, width=80, height=20)
        self.fieldBox.place(x=110, y=200, width=180, height=20)
        self.dateBox.place(x=110, y=300, width=180, height=20)
        self.sendButton.place(x=130, y=400, width=40, height=20)

    def _on_send(self):
        try:
            request = {}
            request['field'] = self.fieldBox.get('0.0', 'end')
            request['date'] = self.dateBox.get('0.0', 'end')
            self.send_queue.put(request)
            self.fieldBox.delete('0.0', 'end')
            self.dateBox.delete('0.0', 'end')
        except Exception as e:
            print(e)

    def _on_close(self):
        self.window.destroy()

    def _show(self):
        try:
            while True:
                msg = self.recv_queue.get()
                self.msgBox.insert('end', msg)
        except Exception as e:
            print(e)

    def _on_recv(self):
        self.recv_proc = Thread(target=self._show)
        self.recv_proc.setDaemon(True)#守护线程
        self.recv_proc.start()
