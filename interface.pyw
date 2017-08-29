# coding=utf-8
import sys
from lib.Interface_pages import App
from lib.QA_util import create_path

# module for the QA interface

reload(sys)
sys.setdefaultencoding('UTF8')

create_path()

app = App()
app.mainloop()
