# coding=utf-8
import sys
from lib.Interface_pages import App
from lib.config import status

# module for the QA interface

reload(sys)
sys.setdefaultencoding('UTF8')

app = App()
app.mainloop()
