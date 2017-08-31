import time
from lib.QA import *

start = time.time()

compare_site_thread_csv("url.csv")
#compare_site_thread("http://www.yummydental.com/", "http://yummydental.televox.west.com/")
#compare_site_selenium("http://www.avonortho.com/", "http://avonortho.televox.west.com/")
#compare_site_selenium_csv("url.csv")

end = time.time()
total = end - start
min = total // 60
sec = total % 60
print("Total time: " + str(min) + " min " + str(sec) + " s.")
