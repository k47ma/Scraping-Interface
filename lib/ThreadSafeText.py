from tkinter import *
import Queue

# module for thread safe textarea


# extend the tkinter Text class
class ThreadSafeText(Text):
    def __init__(self, parent, **kwargs):
        Text.__init__(self, parent, **kwargs)

        self.queue = Queue.Queue()
        self.my_update()

    def write(self, line):
        self.queue.put(line)

    def clear(self):
        self.queue.put(None)

    def my_update(self):
        try:
            while True:
                line = self.queue.get_nowait()
                if line is None:
                    self.delete(1.0, END)
                else:
                    self.insert(END, str(line))
                self.see(END)
                self.update_idletasks()
        except Queue.Empty:
            pass
        try:
            self.after(100, self.my_update)
        except SystemError:
            self.after(100, self.my_update)
