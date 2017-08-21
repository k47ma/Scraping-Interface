from tkinter import *
from config import status
import Queue

# module for thread safe textarea


# extend the tkinter Text class
class ThreadSafeText(Text):
    def __init__(self, parent, queue_name, **kwargs):
        Text.__init__(self, parent, **kwargs)

        self.queue_name = queue_name
        self.my_update()

    def my_update(self):
        try:
            while True:
                queue = status[self.queue_name]
                line = queue.get_nowait()
                if line is None:
                    self.delete(1.0, END)
                else:
                    try:
                        self.insert(END, str(line))
                    except TclError:
                        continue
                self.see(END)
                self.update_idletasks()
        except Queue.Empty:
            pass
        try:
            self.after(100, self.my_update)
        except SystemError:
            self.after(100, self.my_update)
