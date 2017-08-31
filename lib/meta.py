import Queue
import threading
import os
import requests
from bs4 import BeautifulSoup
from config import settings

# testing text output of errors
# testing new commands for input in the text file
# testing support for sites that change siteName, this is already tested a bit, but bugs still could emerge

exit = False
lock = threading.Lock()
result = open('metaResult.txt',
              'w')  # lazy, easier than passing it through all functions, will correct later, I want this file open the entire time; garbage collection will close it for now, adding with for each  write will come later
tellPos = 0


def readNextToken(fileName):
    global tellPos
    newFile = open(fileName, 'r')
    newFile.seek(tellPos, 0)
    flag = False
    str = ""
    while (True):
        if (newFile.tell() < os.stat(fileName).st_size):
            str = str + newFile.read(1)
            tellPos += 1
            if (str[len(str) - 1:] == " " or str[len(str) - 1:] == '\n') and flag:
                flag = True
                if str.strip() != '':
                    return str.strip()
            else:
                flag = True
        else:
            if str.strip() == '':
                flag = True
                tellPos = 0  # returning this value indicates end of file, reset tellPos for next file, READING MULTIPLE FILES UNTESTED
                newFile.close()
                return 'EOF'
            else:
                flag = True
                if str.strip() != '':
                    return str.strip()


class webThread(threading.Thread):
    'Creates a thread for metadata copying'

    def __init__(self, threadID, q, session, newSiteName, blogUrl, oldBlogUrl):
        threading.Thread.__init__(self)
        self.threadID = threadID  # for debugging threading
        self.q = q
        self.session = session
        self.newSiteName = newSiteName
        self.blogUrl = blogUrl
        self.oldBlogUrl = oldBlogUrl

    def run(self):
        copyMeta(self.q, self.session, self.newSiteName, self.blogUrl, self.oldBlogUrl)


def copyMeta(q, session, newSiteName, blogUrl, oldBlogUrl):
    'Takes metadata from page, sends it to televox.west equivalent'
    while not exit:
        lock.acquire()
        if not q.empty():
            url = q.get()
            lock.release()
            site = session.get(url)
            metaHtml = site.content
            if url == oldBlogUrl:
                newUrl = blogUrl
            elif 'blog' in url:
                lastSlash = url.rfind('/', 0, len(url) - 1) + 1  # index after last slash
                if len(url[lastSlash:]) > 50:
                    newUrl = blogUrl + url[lastSlash:lastSlash + 50]
                else:
                    newUrl = blogUrl + url[lastSlash:]
            else:
                startIndex = url.find('://')  # determine if http or https
                friendlyIndex = url.find('.com/') + 5  # finds .com start, goes just after it
                if friendlyIndex == 4:  # cannot find .com(-1) + 5
                    friendlyIndex = url.find('.net/') + 5  # finds .net start, goes just after it
                if friendlyIndex == 4:
                    friendlyIndex = url.find('.org/') + 5
                if friendlyIndex == 4:  # cannot find .com(-1) + 5
                    friendlyIndex = url.find('.us/') + 4
                if friendlyIndex == 3:  # cannot find .com(-1) + 5
                    friendlyIndex = url.find('.com.au/') + len('.com.au/')
                if url[friendlyIndex:].replace('/', '') == 'main' or url[friendlyIndex:].replace('/', '') == 'home':
                    urlFriendly = ''
                else:
                    urlFriendly = url[friendlyIndex:]
                newUrlFull = url[:startIndex] + '://' + newSiteName + '.televox.west.com/' + urlFriendly
                lastSlash = url.rfind('/')
                if len(url[lastSlash:]) > 50:
                    newUrl = newUrlFull[:newUrlFull.rfind('/', 0, len(
                        newUrlFull) - 1) + 51]  # Assuming only last portion will exceed 50 chars
                else:
                    newUrl = newUrlFull
            soup = BeautifulSoup(metaHtml, 'html.parser')
            tempTitle = soup.title.text.encode('utf-8')
            if '&' in tempTitle and 'amp;' not in tempTitle:
                title = tempTitle.replace(';', '')  # bug fix for unencoded ampersands in beautiful soup
            else:
                title = tempTitle
            descriptionLoc = soup.find('meta', {'name': 'description'})
            if descriptionLoc == None:
                description = ''
            else:
                if descriptionLoc['content'][:16] != 'Learn more about' and descriptionLoc['content'][len(
                        descriptionLoc[
                            'content']) - 4:] != '.com':  # if description has 'Learn more about ... .com" but isn't bad -> False positive
                    description = descriptionLoc['content'].encode('utf-8')
                else:
                    description = ''
            keywordsLoc = soup.find('meta', {'name': 'keywords'})
            if keywordsLoc == None:
                keywords = ''
            else:
                keywords = keywordsLoc['content'].encode('utf-8')
            changePageMeta(session, newUrl, title, description, keywords)
        else:
            lock.release()


def login(url):
    username = settings["USER_NAME"]
    password = settings["PASSWORD"]
    index = url.find('.com/') + 5  # will always be .com
    urlStart = url[:index]
    session = requests.Session()
    loginSite = session.get(urlStart + 'gateway/Login.aspx?ReturnUrl=%2f')
    loginHtml = loginSite.content
    loginSoup = BeautifulSoup(loginHtml, 'html.parser')
    viewState = loginSoup.find('input', {'name': '__VIEWSTATE'})['value']
    generator = loginSoup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value']
    values = {'ctl00_RadStyleSheetManager1_TSSM': '',
              'ctl00_ScriptManager1_TSM': '',
              '__EVENTTARGET': '',
              '__EVENTARGUMENT': '',
              '__VIEWSTATE': viewState,
              '__VIEWSTATEGENERATOR': generator,
              'ctl00$ContentPlaceHolder1$txtUsername': username,
              'ctl00$ContentPlaceHolder1$txtPassword': password,
              'ctl00$ContentPlaceHolder1$btnLogin': 'Login'}
    request = session.post(urlStart + 'gateway/Login.aspx?ReturnUrl=%2f', data=values)
    return session


def changePageMeta(session, url, title='', description='', keywords=''):
    index = url.find('.com/') + 5
    if index == 4:  # cannot find .com(-1) + 5
        index = url.find('.net/') + 5
    if index == 4:
        index = url.find('.org/') + 5
    if index == 4:  # cannot find .com(-1) + 5
        index = url.find('.us/') + 4
    if index == 3:  # cannot find (-1) + 4
        index = url.find('.com.au/') + len('.com.au/')
    urlStart = url[:index]
    site = session.get(url)
    if site.status_code == requests.codes.ok:
        pass
    elif site.status_code == 404:
        result.write(url + ' is missing.\r\n')
        return
    else:
        result.write(url + '\r\n')
        result.write(site + '\r\n')
        return
    siteHtml = site.content
    soup = BeautifulSoup(siteHtml, 'html.parser')
    urlEndObject = soup.find('form', {'method': 'post'})
    index = urlEndObject['action'].find('.aspx')
    urlEnd = 'cms/Popup' + urlEndObject['action'][index:] + '&control=PtlPageMetadata'
    if 'https' in urlStart:
        popupUrl = 'http' + urlStart[len('https'):] + urlEnd  # popup always uses http
    else:
        popupUrl = urlStart + urlEnd
    metaPopup = session.get(popupUrl)
    popupHtml = metaPopup.content
    metaSoup = BeautifulSoup(popupHtml, 'html.parser')
    state = metaSoup.find('input', {'name': '__VIEWSTATE'})['value']
    stateGenerator = metaSoup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value']
    inputs = metaSoup.find_all('input')
    txt_232 = ''
    for i in inputs:
        if 'chk_190' in i['name']:
            chk_190 = i['name']
        if 'txt_189' in i['name']:
            txt_189 = i['name']
        if 'txt_143' in i['name']:
            txt_143 = i['name']
        if 'txt_144' in i['name']:
            txt_144 = i['name']
        if 'txt_100' in i['name']:
            txt_100 = i['name']
        if 'txt_232' in i['name']:
            txt_232 = i['name']
    inputs = {'ctl00_ScriptManager1_TSM': '',
              '__EVENTTARGET': '',
              '__EVENTARGUMENT': '',
              '__VIEWSTATE': state,
              '__VIEWSTATEGENERATOR': stateGenerator,
              chk_190: 'on',  # changes name
              txt_189: title,  # changes name
              'ctl00$ContentPlaceHolder1$ctl00$ctl00$txt_98_0': '',
              txt_143: '',  # changes name
              txt_144: '',  # changes name
              txt_100: description,  # changes name
              txt_232: keywords,  # changes name
              'ctl00$ContentPlaceHolder1$ctl00$ctl00$txt_99_0': '',
              'ctl00$ContentPlaceHolder1$ctl00$ctl00$txt_141_0': '',
              'ctl00$ContentPlaceHolder1$ctl00$ctl00$txt_142_0': '',
              'ctl00$ContentPlaceHolder1$ctl00$ctl00$btnSubmit': 'Submit'}
    newReq = session.post(popupUrl, inputs)


def getSiteMeta(url, newUrl=''):
    'Copies meta data from old site to new site'
    content = raw_input('Are you sure you want to do meta for ' + url + '? If not, enter lowercase n\n')
    if content == 'n':
        return
    protoNameStart = url.find('.')
    if protoNameStart == url.find('.',
                                  11):  # 11 is 1st index after http://www., site name will be longer than www, if not potential bug with this
        nameStart = url.find('//') + 1
    else:
        nameStart = protoNameStart
    nameEnd = url.find('.', nameStart + 1)
    siteName = url[nameStart + 1: nameEnd]
    if newUrl == '':
        newUrl = 'http://' + siteName + '.televox.west.com/'
        newSiteName = siteName
    else:
        newNameStart = newUrl.find('//') + 1
        newNameEnd = newUrl.find('.', newNameStart + 1)
        newSiteName = newUrl[newNameStart + 1: newNameEnd]
        if 'tv01stg' in newUrl:  # for testing on staging sites
            newSiteName += '.tv01stg'
    session = login(newUrl)
    sitemap = session.get(url + 'pagesitemap.xml')
    sitemapHtml = sitemap.content
    sitemapSoup = BeautifulSoup(sitemapHtml, 'html.parser')
    linkList = sitemapSoup.find_all('loc')
    newMap = session.get(newUrl + 'sitemap.xml')
    newHtml = newMap.content
    newMapSoup = BeautifulSoup(newHtml, 'html.parser')
    newLinks = newMapSoup.find_all('loc')
    newBlogUrl = ''
    for newLink in newLinks:
        if 'blog' in newLink.text:
            newBlogIndex = newLink.text.find('blog')
            newBlogUrlEnd = newLink.text.find('/', newBlogIndex) + 1  # 1st / after blog, inclusive
            if newBlogUrl.strip() != '' and newBlogUrl != newLink.text[:newBlogUrlEnd]:
                result.write('Potential error with blog url.\r\n')
                result.write('Expected blog url: ' + newBlogUrl + '\r\n')
                result.write('Found blog url: ' + newLink.text[:newBlogUrlEnd] + '\r\n')
            else:
                if newLink.text[:newBlogUrlEnd] != "":
                    newBlogUrl = newLink.text[:newBlogUrlEnd]
                    break
    blogUrl = ''
    for link in linkList:
        if 'blog' in link.text:
            blogIndex = link.text.find('blog')
            blogUrlEnd = link.text.find('/', blogIndex) + 1  # 1st / after blog, inclusive
            if blogUrl != '' and blogUrl != link.text[:blogUrlEnd]:
                result.write('Potential error with blog url.\r\n')
                result.write('Expected blog url: ' + blogUrl + '\r\n')
                result.write('Found blog url: ' + link.text[:blogUrlEnd] + '\r\n')
            else:
                if link.text[:blogUrlEnd].strip() != "":
                    blogUrl = link.text[:blogUrlEnd]
                    break
    blogList = []
    if blogUrl != '':
        blogPage = session.get(blogUrl)
        blogHtml = blogPage.content
        blogSoup = BeautifulSoup(blogHtml, 'html.parser')
        liList = blogSoup.find_all('li', {'class': 'clearfix'})
        for li in liList:
            if len(li.find_all('p')) == 0:
                continue
            a = li.find('a')  # only gets first in clearfix, ASSUMING CLEARFIX CLASS PRESENT
            if a != None:
                blogList.append(a['href'])

    q = Queue.Queue(len(linkList) + len(blogList))
    threads = []
    threadID = 1  # for debugging/ observing threads
    maxThreadNum = 20
    if 20 >= len(linkList) + len(blogList):
        maxThreadNum = len(linkList) + len(blogList)

    for i in range(0, maxThreadNum):
        thread = webThread(threadID, q, session, newSiteName, newBlogUrl, blogUrl)
        thread.start()
        threads.append(thread)
        threadID += 1

    lock.acquire()
    for subpage in linkList:
        if 'blog' not in subpage.text:
            q.put(subpage.text)
    if blogUrl != '' and newBlogUrl != '':
        q.put(blogUrl)
        for blogPost in blogList:
            q.put(blogPost)
    lock.release()

    while not q.empty():
        pass

    global exit
    exit = True

    for thread in threads:
        thread.join()
    exit = False
    print url + ' is finished.'


def getMultipleSiteMeta(txt):
    'Copies over metadata from multiple sites'
    urls = []
    doubleList = []
    while (True):
        readUrl = readNextToken(txt)
        print readUrl
        if readUrl == 'EOF':
            break
        elif readUrl == 'Vertical':
            continue
        elif readUrl == 'Double':
            oldUrl = readNextToken(txt)
            newUrl = readNextToken(txt)
            doubleList.append((oldUrl, newUrl))
        else:
            urls.append(readUrl)
    for site in urls:
        result.write(site + '\r\n')
        getSiteMeta(site)
    for (oldUrl, newUrl) in doubleList:
        result.write(oldUrl + '\r\n')
        getSiteMeta(oldUrl, newUrl)
