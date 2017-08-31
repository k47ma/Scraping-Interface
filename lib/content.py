import os
import threading
import Queue
import requests
from bs4 import BeautifulSoup
from config import settings
from QA_util import create_path

verticalSite = False
exit = False
tellPos = 0
create_path()
result = open('result\\contentResult.txt', 'w')


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
                return 'EOL'
            else:
                flag = True
                if str.strip() != '':
                    return str.strip()


# module for determining the site type
def setVerticalFlag(soup):
    global verticalSite
    template = soup.find('div', id="template")
    try:
        template_class = template.get('class')
    except AttributeError:
        return
    template_class = " ".join(template_class)
    if template_class.find("h_left") != -1 or template_class.find("h_center") != -1 \
            or template_class.find("essential") != -1:
        verticalSite = False
    elif template_class.find("vertical") != -1:
        verticalSite = True


class contentThread(threading.Thread):
    def __init__(self, session, lock, queue, siteName, newSiteName, blogUrl, libraryHtml):
        threading.Thread.__init__(self)
        self.session = session
        self.lock = lock
        self.queue = queue
        self.siteName = siteName
        self.newSiteName = newSiteName
        self.blogUrl = blogUrl
        self.libraryHtml = libraryHtml

    def run(self):
        copyContent(self.session, self.lock, self.queue, self.siteName, self.newSiteName, self.blogUrl,
                    self.libraryHtml)


def copyContent(session, lock, queue, siteName, newSiteName, blogUrl, libraryHtml):
    'Copies content from the old site into the new, assumes pages already created, will print error and quit if not (blog pages assumed created but contentless)'
    global exit
    while not exit:
        with lock:
            if not queue.empty():
                url = queue.get()
            else:
                continue
        site = session.get(url)
        html = site.content
        soup = BeautifulSoup(html, 'html.parser')
        if 'blog' in url:
            return
        lastSlash = url.rfind('/', 0, len(url) - 2) + 1  # index after last slash
        if len(url[lastSlash:]) > 50:
            newUrl = blogUrl + url[lastSlash:lastSlash + 50]
        else:
            newUrl = blogUrl + url[lastSlash:]
        article = soup.find('article')
        try:
            [x.extract() for x in article.find_all('header')]
        except:
            print url + ' failed to get article.'
            result.write(url + ' failed to get article.\r\n')
            return
        imgs = article.find_all('img')
        migratedImages = getImages(session, url, newUrl, newSiteName, libraryHtml)
        j = 0
        length = 0
        flag = True
        for img in imgs:
            if img.has_attr('src') and (siteName in img['src'] or 'televox' in img['src'] or img['src'][:1] == '/'):
                length += 1
        for img in imgs:
            if img.has_attr('objectid'):
                del (img['objectid'])
            if img.has_attr('imagesiteid'):
                del (img['imagesiteid'])
            if not img.has_attr('alt') or img['alt'] == '':
                imgNameStart = img['src'].rfind('/') + 1
                img['alt'] = img['src'][imgNameStart:]
            if (len(migratedImages) == length or len(migratedImages) == 10) and j < 10:
                flag = False
                if img.has_attr('src') and (siteName in img['src'] or 'televox' in img['src'] or img['src'][
                                                                                                 :1] == '/'):  # relying on shortcircuiting to save me if no src present
                    img['src'] = '/common/pages/UserFile.aspx?fileId=' + migratedImages[
                        j]  # if even one of the image's src was fixed before; disaster, ASSUMES ORDER
                    j += 1
            else:
                if img.has_attr('src') and (
                            siteName in img['src'] or 'televox' in img['src'] or img['src'][:1] == '/'):
                    j += 1
        if j and flag:
            print str(j) + ' images were required, at ' + newUrl + ' these were the result: ' + str(migratedImages)
            result.write(str(j) + ' images were required, at ' + newUrl + ' these were the result: ' + str(
                migratedImages) + '\r\n')
        anchors = article.find_all('a')
        for anchor in anchors:
            href = anchor['href']
            if href[:1] == '/':
                pageNameSlash = href.rfind('/', 0, len(href) - 1)
                pageName = href[pageNameSlash:].replace('/', '')
                possibleDuplicate = href[href.rfind('/', 0, pageNameSlash):pageNameSlash].replace('/', '')
                if pageName == possibleDuplicate:
                    anchor['href'] = href[:pageNameSlash]
                    href = anchor['href']
            if siteName in href and 'facebook' not in href and 'File' not in href and 'Image' not in href and 'Library' not in href and 'mailto:' not in href:
                siteUrlEnd = href.find('/', href.find(siteName))
                if siteUrlEnd == -1:
                    anchor['href'] = '/'
                    continue
                pageNameSlash = href.rfind('/', 0, len(href) - 1)
                pageName = href[pageNameSlash:].replace('/', '')
                possibleDuplicate = href[href.rfind('/', 0, pageNameSlash):pageNameSlash].replace('/', '')
                if pageName == possibleDuplicate:
                    anchor['href'] = href[siteUrlEnd:pageNameSlash]
                else:
                    anchor['href'] = href[siteUrlEnd:]
                content = str(article)
                # try:
                modifyBlogPost(session, newUrl, content)
            # except Exception, e:
            #	print str(e)
            #	print url + ' failed. Check if page is missing. Home page will not work'
            else:
                startIndex = url.find('://')  # determine if http or https
                friendlyIndex = url.find('.com/') + 5  # finds .com start, goes just after it
                if friendlyIndex == 4:  # cannot find .com(-1) + 5
                    friendlyIndex = url.find('.net/') + 5  # finds .net start, goes just after it
                if friendlyIndex == 4:  # cannot find .com(-1) + 5
                    friendlyIndex = url.find('.org/') + 5
                if friendlyIndex == 4:  # cannot find .com(-1) + 5
                    friendlyIndex = url.find('.us/') + 4
                if friendlyIndex == 3:  # cannot find .com(-1) + 5
                    friendlyIndex = url.find('.com.au/') + len('.com.au/')
                newUrlFull = url[:startIndex] + '://' + newSiteName + '.televox.west.com/' + url[friendlyIndex:]
                lastSlash = url.rfind('/')
                if len(url[lastSlash:]) > 50:
                    newUrl = newUrlFull[:newUrlFull.rfind('/', 0, len(
                        newUrlFull) - 1) + 51]  # Assuming only last portion will exceed 50 chars, extra 1 gets past slash
                else:
                    newUrl = newUrlFull  # python does not allow for strings to be modified (can be added to though, new copies can be made)
                try:
                    print newUrl
                    newSite = session.get(newUrl + '?action=design')
                    newSite.raise_for_status()
                except:
                    print 'New url not there for: ' + url
                    result.write('New url not there for: ' + url + '\r\n')
                    return
                newHtml = newSite.content
                newSoup = BeautifulSoup(newHtml, 'html.parser')
                spans = newSoup.find_all('span')
                for span in spans:  # this detects the presence of existing portlets, stops if one is there
                    if span.has_attr('onclick') and 'window.location' in span['onclick']:
                        return
                contentDiv = soup.find('div', {'id': 'content'})
                divs = contentDiv.find_all('div')
                iappsContainers = []
                for div in divs:
                    if div.has_attr('class') and (
                            div['class'] == 'iapps-container-container' or div['class'] == [u'iapps-container-container']):
                        iappsContainers.append(div)
                    if div.has_attr('id') and 'TxtContentOverview_ctl' in div['id']:
                        iappsContainers.append(div)
                if len(iappsContainers) == 0:
                    element = contentDiv.find('p')
                    while element.name != 'div' or not element.has_attr('id') or 'ct' not in element[
                        'id'] or element.parent == None:
                        element = element.parent
                    imgs = element.find_all('img')
                    migratedImages = getImages(session, url, newUrl, newSiteName, libraryHtml)
                    j = 0
                    length = 0
                    flag = True
                    for img in imgs:
                        if img.has_attr('src') and (
                                    siteName in img['src'] or 'televox' in img['src'] or img['src'][:1] == '/'):
                            length += 1
                    for img in imgs:
                        if img.has_attr('objectid'):
                            del (img['objectid'])
                        if img.has_attr('imagesiteid'):
                            del (img['imagesiteid'])
                        if not img.has_attr('alt') or img['alt'] == '':
                            imgNameStart = img['src'].rfind('/') + 1
                            img['alt'] = img['src'][imgNameStart:]
                        if (len(migratedImages) == length or len(migratedImages) == 10) and j < 10:
                            flag = False
                            if img.has_attr('src') and (siteName in img['src'] or 'televox' in img['src'] or img['src'][
                                                                                                             :1] == '/'):  # relying on shortcircuiting to save me if no src present
                                img['src'] = '/common/pages/UserFile.aspx?fileId=' + migratedImages[
                                    j]  # if even one of the image's src was fixed before; disaster, ASSUMES ORDER
                                j += 1
                        else:
                            if img.has_attr('src') and (
                                        siteName in img['src'] or 'televox' in img['src'] or img['src'][:1] == '/'):
                                j += 1
                    if j and flag:
                        print str(j) + ' images were required, at ' + newUrl + ' these were the result: ' + str(
                            migratedImages)
                        result.write(str(j) + ' images were required, at ' + newUrl + ' these were the result: ' + str(
                            migratedImages) + '\r\n')
                    anchors = element.find_all('a')
                    for anchor in anchors:
                        href = anchor['href']
                        if href[:1] == '/':
                            pageNameSlash = href.rfind('/', 0, len(href) - 1)
                            pageName = href[pageNameSlash:].replace('/', '')
                            possibleDuplicate = href[href.rfind('/', 0, pageNameSlash):pageNameSlash].replace('/', '')
                            if pageName == possibleDuplicate:
                                anchor['href'] = href[:pageNameSlash]
                                href = anchor['href']
                        if siteName in href and 'facebook' not in href and 'File' not in href and 'Image' not in href and 'Library' not in href and 'mailto:' not in href:
                            href = anchor['href']
                            siteUrlEnd = href.find('/', href.find(siteName))
                            if siteUrlEnd == -1:
                                anchor['href'] = '/'
                                continue
                            pageNameSlash = href.rfind('/', 0, len(href) - 1)
                            pageName = href[pageNameSlash:].replace('/', '')
                            possibleDuplicate = href[href.rfind('/', 0, pageNameSlash):pageNameSlash].replace('/', '')
                            if pageName == possibleDuplicate:
                                anchor['href'] = href[siteUrlEnd:pageNameSlash]
                            else:
                                anchor['href'] = href[siteUrlEnd:]
                    content = str(element)
                    title = url[friendlyIndex:]
                    try:
                        if content != None:
                            addPortlet(session, newUrl)
                            submitContent(session, newUrl, content, title)
                    except Exception, e:
                        print str(e)
                        print url + ' failed. Check if page is missing. Home page will not work'
                        result.write(str(e) + '\r\n')
                        result.write(url + ' failed. Check if page is missing. Home page will not work\r\n')
                else:
                    imgs = []
                    j = 0
                    flag = True
                    for iappsContainer in iappsContainers:
                        imgs.extend(iappsContainer.find_all('img'))
                    for i in range(0, len(iappsContainers)):
                        element = iappsContainers[i]
                        migratedImages = getImages(session, url, newUrl, newSiteName, libraryHtml)
                        length = 0
                        for img in imgs:
                            if img.has_attr('src') and (
                                        siteName in img['src'] or 'televox' in img['src'] or img['src'][:1] == '/'):
                                length += 1
                        for img in imgs:
                            if img.has_attr('objectid'):
                                del (img['objectid'])
                            if img.has_attr('imagesiteid'):
                                del (img['imagesiteid'])
                            if not img.has_attr('alt') or img['alt'] == '':
                                imgNameStart = img['src'].rfind('/') + 1
                                img['alt'] = img['src'][imgNameStart:]
                            if (len(migratedImages) == length or len(migratedImages) == 10) and j < 10:
                                flag = False
                                if img.has_attr('src') and (siteName in img['src'] or 'televox' in img['src'] or img['src'][
                                                                                                                 :1] == '/'):  # relying on shortcircuiting to save me if no src present
                                    img['src'] = '/common/pages/UserFile.aspx?fileId=' + migratedImages[
                                        j]  # if even one of the image's src was fixed before; disaster, ASSUMES ORDER
                                    j += 1
                            else:
                                if img.has_attr('src') and (
                                            siteName in img['src'] or 'televox' in img['src'] or img['src'][:1] == '/'):
                                    j += 1
                        anchors = element.find_all('a')
                        for anchor in anchors:
                            href = anchor['href']
                            if href[:1] == '/':
                                pageNameSlash = href.rfind('/', 0, len(href) - 1)
                                pageName = href[pageNameSlash:].replace('/', '')
                                possibleDuplicate = href[href.rfind('/', 0, pageNameSlash):pageNameSlash].replace('/', '')
                                if pageName == possibleDuplicate:
                                    anchor['href'] = href[:pageNameSlash]
                                    href = anchor['href']
                            if siteName in href and 'facebook' not in href and 'File' not in href and 'Image' not in href and 'Library' not in href and 'mailto:' not in href:
                                siteUrlEnd = href.find('/', href.find(siteName))
                                if siteUrlEnd == -1:
                                    anchor['href'] = '/'
                                    continue
                                pageNameSlash = href.rfind('/', 0, len(href) - 1)
                                pageName = href[pageNameSlash:].replace('/', '')
                                possibleDuplicate = href[href.rfind('/', 0, pageNameSlash):pageNameSlash].replace('/', '')
                                if pageName == possibleDuplicate:
                                    anchor['href'] = href[siteUrlEnd:pageNameSlash]
                                else:
                                    anchor['href'] = href[siteUrlEnd:]
                        content = str(element)
                        title = url[friendlyIndex:]
                        if i > 0:
                            title += str(i)
                        try:
                            if content != None:
                                addPortlet(session, newUrl, 'content', i)
                                submitContent(session, newUrl, content, title, i)
                        except:
                            print url + ' failed. Check if page is missing.'
                            result.write(url + ' failed. Check if page is missing.\r\n')
                    if j and flag:
                        print str(j) + ' images were required, at ' + newUrl + ' these were the result: ' + str(
                            migratedImages)
                        result.write(str(j) + ' images were required, at ' + newUrl + ' these were the result: ' + str(
                            migratedImages) + '\r\n')


def getImages(session, url, newUrl, newSiteName, libraryHtml):
    'Returns a list of folder IDs, which can be used to find min (root) and max ID (newest)'
    urlStart = newUrl[:newUrl.find('.com/') + len('.com/')]
    libraryUrl = urlStart + 'common/plugins/RadEditorAjax/SharedImageLibrary/SharedImageLibrary.aspx'
    # libraryHtml = session.get(libraryUrl).content
    librarySoup = BeautifulSoup(libraryHtml, 'html.parser')
    viewState = librarySoup.find('input', {'name': '__VIEWSTATE'})['value']
    generator = librarySoup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value']
    data = {
        'radManager_TSM': ';;AjaxControlToolkit, Version=4.1.40412.0, Culture=neutral, PublicKeyToken=28f01b0e84b6d53e:en-US:acfc7575-cdee-46af-964f-5d85d9cdcf92:ea597d4b:b25378d2',
        '__EVENTTARGET': 'ddlView',
        '__EVENTARGUMENT': '',
        '__LASTFOCUS': '',
        '__VIEWSTATE': viewState,
        '__VIEWSTATEGENERATOR': generator,
        'ddlView': 'local',
        'radGridClickedRowIndex': '',
        'hdfPlugin': 'true',
        'hdSelectedTreeNode': '54159',  # this is root of global, constant across all sites; do not send to
        'FolderTreeView_ClientState': '{"expandedNodes":[],"collapsedNodes":[],"logEntries":[],"selectedNodes":["0"],"checkedNodes":[],"scrollPosition":0}',
        'uploader_count': '0',
        'RadPopup_ClientState': '',
        'RadWM_ClientState': '',
        'rpTreeview_ClientState': '{"_originalWidth":"180px","_originalHeight":"428px","_collapsedDirection":1,"_scrollLeft":0,"_scrollTop":0,"_expandedSize":0,"width":180,"height":428,"collapsed":false,"contentUrl":"","minWidth":20,"maxWidth":10000,"minHeight":20,"maxHeight":10000,"locked":false}',
        'splitBar1_ClientState': '',
        'rdGridList_rghcMenu_ClientState': '',
        'rdGridList_ClientState': '',
        'ListContextMenu_ClientState': '',
        'hdSelectedFileId': '0',
        'hdSelectedFileName': '',
        'rpFileList_ClientState': '{"_originalWidth":"200px","_originalHeight":"428px","_collapsedDirection":1,"_scrollLeft":0,"_scrollTop":0,"_expandedSize":0,"width":200,"height":428,"collapsed":false,"contentUrl":"","minWidth":20,"maxWidth":10000,"minHeight":20,"maxHeight":10000,"locked":false}',
        'splitBar2_ClientState': '',
        'radTabProperty_ClientState': '{"selectedIndexes":["0"],"logEntries":[],"scrollState":{}}',
        'txtAlt': '',
        'radMPProperty_ClientState': '',
        'rpProperty_ClientState': '{"_originalWidth":"288px","_originalHeight":"428px","_collapsedDirection":1,"_scrollLeft":0,"_scrollTop":0,"_expandedSize":0,"width":288,"height":428,"collapsed":false,"contentUrl":"","minWidth":20,"maxWidth":10000,"minHeight":20,"maxHeight":10000,"locked":false}',
        'RadSplitter_ClientState': ''}
    request = session.post(libraryUrl, data)
    request.raise_for_status()
    content = request.content
    contentSoup = BeautifulSoup(content, 'html.parser')
    folders = []
    currentIndex = content.find('nodeData')
    stopIndex = content.find('selectedIndexes')
    while True:
        start = content.find('value', currentIndex) + len('value') + 3
        end = content.find('}', start) - 1
        if ',' in content[start:end]:
            end = content.find(',', start) - 1
        currentIndex = end
        if currentIndex > stopIndex:
            break
        folderID = int(content[start:end])
        folders.append(folderID)
    folderNames = contentSoup.find_all('span', {'class': 'rtIn'})
    i = 0
    parentID = ''
    longestFolder = ''
    longestFolderNum = -1
    for folderName in folderNames:
        friendlyIndex = url.find('/', url.find(newSiteName))
        desiredFolderName = url[friendlyIndex + 1:].replace('/', ' ').strip()
        if desiredFolderName in folderName.text and len(folderName.text) > len(longestFolder):
            longestFolder = folderName.text.strip()
            longestFolderNum = i
        i += 1
    if longestFolderNum == -1:
        return []
    else:
        parentID = folders[longestFolderNum]
    desiredFolderData = {
        'radManager_TSM': ';;AjaxControlToolkit, Version=4.1.40412.0, Culture=neutral, PublicKeyToken=28f01b0e84b6d53e:en-US:acfc7575-cdee-46af-964f-5d85d9cdcf92:ea597d4b:b25378d2',
        '__EVENTTARGET': 'FolderTreeView',
        '__EVENTARGUMENT': '{"commandName":"Click","index":"0:' + str(longestFolderNum - 1) + '"}',
        # file num on level under local content library
        '__LASTFOCUS': '',
        '__VIEWSTATE': viewState,
        '__VIEWSTATEGENERATOR': generator,
        'ddlView': 'local',
        'radGridClickedRowIndex': '',
        'hdfPlugin': 'true',
        'hdSelectedTreeNode': parentID,
        'FolderTreeView_ClientState': '{"expandedNodes":[],"collapsedNodes":[],"logEntries":[],"selectedNodes":["0"],"checkedNodes":[],"scrollPosition":0}',
        'uploader_count': '0',
        'RadPopup_ClientState': '',
        'RadWM_ClientState': '',
        'rpTreeview_ClientState': '{"_originalWidth":"180px","_originalHeight":"428px","_collapsedDirection":1,"_scrollLeft":0,"_scrollTop":0,"_expandedSize":0,"width":180,"height":428,"collapsed":false,"contentUrl":"","minWidth":20,"maxWidth":10000,"minHeight":20,"maxHeight":10000,"locked":false}',
        'splitBar1_ClientState': '',
        'rdGridList_rghcMenu_ClientState': '',
        'rdGridList_ClientState': '',
        'ListContextMenu_ClientState': '',
        'hdSelectedFileId': '0',
        'hdSelectedFileName': '',
        'rpFileList_ClientState': '{"_originalWidth":"200px","_originalHeight":"428px","_collapsedDirection":1,"_scrollLeft":0,"_scrollTop":0,"_expandedSize":0,"width":200,"height":428,"collapsed":false,"contentUrl":"","minWidth":20,"maxWidth":10000,"minHeight":20,"maxHeight":10000,"locked":false}',
        'splitBar2_ClientState': '',
        'radTabProperty_ClientState': '{"selectedIndexes":["0"],"logEntries":[],"scrollState":{}}',
        'txtAlt': '',
        'radMPProperty_ClientState': '',
        'rpProperty_ClientState': '{"_originalWidth":"288px","_originalHeight":"428px","_collapsedDirection":1,"_scrollLeft":0,"_scrollTop":0,"_expandedSize":0,"width":288,"height":428,"collapsed":false,"contentUrl":"","minWidth":20,"maxWidth":10000,"minHeight":20,"maxHeight":10000,"locked":false}',
        'RadSplitter_ClientState': ''}
    imageRequest = session.post(libraryUrl, desiredFolderData)
    imageRequest.raise_for_status()
    imageContent = imageRequest.content
    images = []
    imageListIndex = imageContent.find('_clientKeyValues')
    lastImageIndex = imageContent.find('_controlToFocus')
    while True:
        imageStart = imageContent.find('"id"', imageListIndex) + len('"id"') + 2
        imageEnd = imageContent.find(',', imageStart) - 1
        imageListIndex = imageEnd
        if imageListIndex > lastImageIndex:
            break
        imageID = imageContent[imageStart:imageEnd]
        images.append(imageID)
    return images


def login(url):
    username = settings["USER_NAME"]
    password = settings["PASSWORD"]
    index = url.find('.com/') + 5
    urlStart = url[:index]
    session = requests.Session()
    loginSite = session.get(urlStart + 'gateway/Login.aspx?ReturnUrl=%2f')
    loginSite.raise_for_status()
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
    request = session.post(urlStart + 'gateway/Login.aspx?ReturnUrl=%2f', values)
    return session


def addPortlet(session, url, portletType='content', order=0):
    index = url.find('.com/') + 5
    urlStart = url[:index]
    requestUrl = urlStart + 'portal/svc/PtlSvc.asmx/AddPortletInstance'
    portletTypes = {'content': 231, 'form': 53834, 'map': 53837, 'advanced_data_display': 55268, 'site_navigation': 260}
    try:
        portletID = portletTypes[portletType]
    except:
        print "Invalid portlet type, only the following portlet types are implemented:"
        print 'content, form, map, advanced_data_display, site_navigation, spelt like these while using.'
        result.write("Invalid portlet type, only the following portlet types are implemented:\r\n")
        result.write('content, form, map, advanced_data_display, site_navigation, spelt like these while using.\r\n')
        return
    try:
        site = session.get(url + '?action=design')
        site.raise_for_status()
    except:
        print url + ' failed'
        result.write(url + ' failed\r\n')
    html = site.content
    soup = BeautifulSoup(html, 'html.parser')
    formVal = soup.find('form', {'id': 'aspnetForm'})['action']
    start = formVal.find('pageId=') + len('pageId=')
    end = formVal.find('&', start)  # finds 1st & after value
    pageID = formVal[start:end]
    divs = soup.find_all('div')
    for div in divs:
        if div.has_attr('column_id'):
            columnID = div['column_id']
            break
    data = {'stringPortletId': portletID,
            'stringColumnId': columnID,
            'columnOrder': order,
            'pageId': pageID}
    request = session.post(requestUrl, data)


def submitContent(session, url, content='', title='default', portletNum=0):
    'Changes the content of an existing portlet, if it targets a non content portlet, nothing happens'
    index = url.find('.com/') + 5  # new sites always end in .com
    urlStart = url[:index]
    site = session.get(url + '?action=design')
    siteHtml = site.content
    mainSoup = BeautifulSoup(siteHtml, 'html.parser')
    submitFriendly = []
    spans = mainSoup.find_all('span')
    for span in spans:
        if span.has_attr('onclick') and 'window.location' in span['onclick']:
            submitFriendly.append(span['onclick'][len('window.location') + 3:len(span['onclick']) - 2])
    submitUrl = urlStart + submitFriendly[portletNum]
    formVal = mainSoup.find('form', {'id': 'aspnetForm'})['action']
    start = formVal.find('pageId=') + len('pageId=')
    end = formVal.find('&', start)  # finds 1st & after value
    pageID = formVal[start:end]
    inputs = mainSoup.find_all('input')
    for Input in inputs:
        if Input.has_attr('name') and Input['name'][len(Input['name']) - len('hdPopupUrl'):] == 'hdPopupUrl':
            popupUrl = Input['value']
            break
    state = mainSoup.find('input', {'name': '__VIEWSTATE'})['value']
    stateGenerator = mainSoup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value']
    localContentSite = session.get(urlStart + '/televox/LocalPortletLibrary.aspx')
    localContentHtml = localContentSite.content
    localContentSoup = BeautifulSoup(localContentHtml, 'html.parser')
    scripts = localContentSoup.find_all('script')
    rootID = '0'
    parentID = '0'
    try:
        for script in scripts:
            if 'nodeData' in script.text:
                rootIndex = script.text.find(
                    'value')  # root will be the first result, next results will be folders, one for each on folder tree
                rootID = script.text[rootIndex + len('value') + 3:script.text.find('"', rootIndex + len('value') + 3)]
                parentIndex = script.text.find('value', rootIndex + len('value'))  # finds next folder
                collapseAnimationIndex = script.text.find('collapseAnimation', rootIndex + len('value'))
                if collapseAnimationIndex < parentIndex:
                    print 'Nowhere to save to, empty portlet will be left and content will be unchanged'
                    result.write('Nowhere to save to, empty portlet will be left and content will be unchanged\r\n')
                    return
                else:
                    parentID = script.text[
                               parentIndex + len('value') + 3:script.text.find('"', parentIndex + len('value') + 3)]
    except:
        print 'Could not find save info, did not save.'
        result.write('Could not find save info, did not save.\r\n')
        return
    global verticalSite
    if verticalSite:
        inputs = {'ctl00_RadStyleSheetManager1_TSSM': '',
                  'ctl00_ScriptManager1_TSM': '',
                  '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$ctl02$ctl46$ctl00$ibTelevoxSaveAsTop',
                  '__EVENTARGUMENT': 'undefined',
                  '__VIEWSTATE': state,
                  '__VIEWSTATEGENERATOR': stateGenerator,
                  'ctl00_ContentPlaceHolder1_RadWindowManagerLoadingContentTree_ClientState': '',
                  'ctl00_ContentPlaceHolder1_RadWindowLoadingContentTree_ClientState': '',
                  'ctl00_ContentPlaceHolder1_RadWindowPermissionControl_ClientState': '',
                  'ctl00_ContentPlaceHolder1_ctl00_RadWND_ClientState': '',
                  # 'ctl00_ContentPlaceHolder1_ctl01_radmenu_ClientState':'', #not necessary in vertical? not there in test submission
                  'ctl00$ContentPlaceHolder1$ctl02$hfReleaseDate': '',
                  'ctl00$ContentPlaceHolder1$ctl02$hfExiryDate': '',
                  'ctl00$ContentPlaceHolder1$ctl02$ctl46$ctl00$hdRootId': rootID,
                  'ctl00$ContentPlaceHolder1$ctl02$ctl46$ctl00$hdParentSelectedId': parentID,
                  'ctl00$ContentPlaceHolder1$ctl02$ctl46$ctl00$hdFileName': '',
                  'ctl00$ContentPlaceHolder1$ctl02$ctl46$ctl00$hdSelectedFileId': '0',
                  'ctl00$ContentPlaceHolder1$ctl02$ctl46$ctl00$hdPopupUrl': popupUrl,
                  'ctl00$ContentPlaceHolder1$ctl02$ctl46$ctl00$hdInlineEditor': 'false',
                  'ctl00$ContentPlaceHolder1$ctl02$ctl46$ctl00$hdInlineContent': '',
                  'ctl00$ContentPlaceHolder1$ctl02$ctl46$ctl00$hdCustomerSite': '1',
                  'ctl00$ContentPlaceHolder1$ctl02$ctl46$ctl00$txtTitle': title,  # have to choose this
                  'ctl00_ContentPlaceHolder1_ctl02_ctl46_ctl00_reEditArea_ctl00_dialogOpener_Window_ClientState': '',
                  'ctl00_ContentPlaceHolder1_ctl02_ctl46_ctl00_reEditArea_ctl00_dialogOpener_ClientState': '',
                  'ctl00$ContentPlaceHolder1$ctl02$ctl46$ctl00$reEditArea$ctl00': content,
                  'ctl00_ContentPlaceHolder1_ctl02_ctl46_ctl00_reEditArea_ctl00_ClientState': '',
                  # 'ctl00_ContentPlaceHolder1_ctl02_ctl46_ctl00$ibTelevoxSaveBottom':'Save', #for modifying, also saveasyop at top to savetop if modifying
                  'ctl00_ContentPlaceHolder1_ctl02_ctl46_ctl00_RadWindowLoadingContentFolderTree_ClientState': ''}
    else:
        inputs = {'ctl00_RadStyleSheetManager1_TSSM': '',
                  'ctl00_ScriptManager1_TSM': '',
                  '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$ctl07$ctl46$ctl00$ibTelevoxSaveAsTop',
                  '__EVENTARGUMENT': 'undefined',
                  '__VIEWSTATE': state,
                  '__VIEWSTATEGENERATOR': stateGenerator,
                  'ctl00_ContentPlaceHolder1_RadWindowManagerLoadingContentTree_ClientState': '',
                  'ctl00_ContentPlaceHolder1_RadWindowLoadingContentTree_ClientState': '',
                  'ctl00_ContentPlaceHolder1_RadWindowPermissionControl_ClientState': '',
                  'ctl00_ContentPlaceHolder1_ctl00_RadWND_ClientState': '',
                  'ctl00_ContentPlaceHolder1_ctl01_radmenu_ClientState': '',
                  'ctl00$ContentPlaceHolder1$ctl07$hfReleaseDate': '',
                  'ctl00$ContentPlaceHolder1$ctl07$hfExiryDate': '',
                  'ctl00$ContentPlaceHolder1$ctl07$ctl46$ctl00$hdRootId': rootID,
                  'ctl00$ContentPlaceHolder1$ctl07$ctl46$ctl00$hdParentSelectedId': parentID,
                  'ctl00$ContentPlaceHolder1$ctl07$ctl46$ctl00$hdFileName': '',
                  'ctl00$ContentPlaceHolder1$ctl07$ctl46$ctl00$hdSelectedFileId': '0',
                  'ctl00$ContentPlaceHolder1$ctl07$ctl46$ctl00$hdPopupUrl': popupUrl,
                  'ctl00$ContentPlaceHolder1$ctl07$ctl46$ctl00$hdInlineEditor': 'false',
                  'ctl00$ContentPlaceHolder1$ctl07$ctl46$ctl00$hdInlineContent': '',
                  'ctl00$ContentPlaceHolder1$ctl07$ctl46$ctl00$hdCustomerSite': '1',
                  'ctl00$ContentPlaceHolder1$ctl07$ctl46$ctl00$txtTitle': title,  # have to choose this
                  'ctl00_ContentPlaceHolder1_ctl07_ctl46_ctl00_reEditArea_ctl00_dialogOpener_Window_ClientState': '',
                  'ctl00_ContentPlaceHolder1_ctl07_ctl46_ctl00_reEditArea_ctl00_dialogOpener_ClientState': '',
                  'ctl00$ContentPlaceHolder1$ctl07$ctl46$ctl00$reEditArea$ctl00': content,
                  'ctl00_ContentPlaceHolder1_ctl07_ctl46_ctl00_reEditArea_ctl00_ClientState': '',
                  # 'ctl00_ContentPlaceHolder1_ctl07_ctl46_ctl00$ibTelevoxSaveBottom':'Save', #for modifying, also saveasyop at top to savetop if modifying
                  'ctl00_ContentPlaceHolder1_ctl07_ctl46_ctl00_RadWindowLoadingContentFolderTree_ClientState': ''}
    newReq = session.post(submitUrl, inputs)  # span with onclick starts with window.location=, one for every portlet
    newReq.raise_for_status()


def modifyBlogPost(session, url, content='', summary='', date=''):
    'Edits an advanced data display given a url, if no value is given in the optional params, it will keep old values'
    try:
        site = session.get(url + '?action=design')
        site.raise_for_status()
    except:
        print url + ' failed.'
        result.write(url + ' failed.\r\n')
        return
    siteHtml = site.content
    siteSoup = BeautifulSoup(siteHtml, 'html.parser')
    portlet = siteSoup.find('div', {'class': 'portlet_instance'})  # finds first, blog pages should not have 2
    editLink = portlet.find('a', {'title': 'Edit'})
    editUrl = url[:url.find('.com/') + 4] + editLink['href']
    editSite = session.get(editUrl)
    editHtml = editSite.content
    editSoup = BeautifulSoup(editHtml, 'html.parser')
    viewState = editSoup.find('input', {'id': '__VIEWSTATE'})['value']
    generator = editSoup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value']
    global verticalSite
    if verticalSite:
        siteNum = '02'
    else:
        siteNum = '07'
    titleTag = editSoup.find('input', {'name': 'ctl00$ContentPlaceHolder1$ctl' + siteNum + '$ctl47$field_title'})
    if titleTag.has_attr('value'):
        title = titleTag['value']
    else:
        title = ''
    imageTag = editSoup.find('input',
                             {'name': 'ctl00$ContentPlaceHolder1$ctl' + siteNum + '$ctl47$field_featured_image_link'})
    if imageTag.has_attr('value'):
        image = imageTag['value']
    else:
        image = ''
    imageTitleTag = editSoup.find('input',
                                  {'name': 'ctl00$ContentPlaceHolder1$ctl' + siteNum + '$ctl47$field_image_title'})
    if imageTitleTag.has_attr('value'):
        imageTitle = imageTitleTag['value']
    else:
        imageTitle = ''
    if summary == '':
        summaryTag = editSoup.find('input',
                                   {'name': 'ctl00$ContentPlaceHolder1$ctl' + siteNum + '$ctl47$field_summary'})
        if summaryTag.has_attr('value'):
            summary = summaryTag['value']
        else:
            summary = ''
    dateTag = editSoup.find('input',
                            {'name': 'ctl00$ContentPlaceHolder1$ctl' + siteNum + '$ctl47$field_published_date'})
    if dateTag.has_attr('value'):
        date = dateTag['value']
    else:
        date = ''
    fullDateTag = editSoup.find('input', {
        'name': 'ctl00$ContentPlaceHolder1$ctl' + siteNum + '$ctl47$field_published_date$dateInput'})
    if fullDateTag.has_attr('value'):
        fullDate = fullDateTag['value']
    else:
        fullDate = ''
    dateList = editSoup.find('input', {
        'name': 'ctl00_ContentPlaceHolder1_ctl' + siteNum + '_ctl47_field_published_date_calendar_AD'})['value']
    if content == '':
        contentTag = editSoup.find('input',
                                   {'name': 'ctl00$ContentPlaceHolder1$ctl' + siteNum + '$ctl47$field_body$ctl00'})
        if contentTag.has_attr('value'):
            content = contentTag['value']
        else:
            content = ''
    lastModifiedDate = \
    editSoup.find('input', {'name': 'ctl00$ContentPlaceHolder1$ctl' + siteNum + '$ctl47$field_pageLastModified_date'})[
        'value']
    fullLastModifiedDate = editSoup.find('input', {
        'name': 'ctl00$ContentPlaceHolder1$ctl' + siteNum + '$ctl47$field_pageLastModified_date$dateInput'})['value']
    lastModifiedDateList = editSoup.find('input', {
        'name': 'ctl00_ContentPlaceHolder1_ctl' + siteNum + '_ctl47_field_pageLastModified_date_calendar_AD'})['value']
    publishedDateDict = '{"enabled":true,"emptyMessage":"","validationText":"' + date + '-00-00-00","valueAsString":"' + date + '-00-00-00","minDateStr":"1000-01-01-00-00-00","maxDateStr":"9999-12-31-00-00-00","lastSetTextBoxValue":"' + fullDate + '"}'
    modifiedDateDict = '{"enabled":false,"emptyMessage":"","validationText":"' + lastModifiedDate + '-00-00-00","valueAsString":"' + lastModifiedDate + '-00-00-00","minDateStr":"1000-01-01-00-00-00","maxDateStr":"9999-12-31-00-00-00","lastSetTextBoxValue":"' + fullLastModifiedDate + '"}'
    data = {'ctl00_RadStyleSheetManager1_TSSM': '',
            'ctl00_ScriptManager1_TSM': '',
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': viewState,
            '__VIEWSTATEGENERATOR': generator,
            'ctl00_ContentPlaceHolder1_RadWindowManagerLoadingContentTree_ClientState': '',
            'ctl00_ContentPlaceHolder1_RadWindowLoadingContentTree_ClientState': '',
            'ctl00_ContentPlaceHolder1_RadWindowPermissionControl_ClientState': '',
            'ctl00_ContentPlaceHolder1_ctl00_RadWND_ClientState': '',
            'ctl00_ContentPlaceHolder1_ctl01_radmenu_ClientState': '',
            'ctl00$ContentPlaceHolder1$ctl' + siteNum + '$hfReleaseDate': '',
            'ctl00$ContentPlaceHolder1$ctl' + siteNum + '$hfExiryDate': '',
            'ctl00$ContentPlaceHolder1$ctl' + siteNum + '$ctl47$hfClientId': '',
            'ctl00$ContentPlaceHolder1$ctl' + siteNum + '$ctl47$field_title': title,  # will need to extract this
            'ctl00$ContentPlaceHolder1$ctl' + siteNum + '$ctl47$field_featured_image_link': image,
            # will need to extract this
            'ctl00$ContentPlaceHolder1$ctl' + siteNum + '$ctl47$field_featured_image_hiddenId': '',
            'ctl00$ContentPlaceHolder1$ctl' + siteNum + '$ctl47$field_image_title': imageTitle,  # need to extract
            'ctl00$ContentPlaceHolder1$ctl' + siteNum + '$ctl47$field_summary': summary,  # param
            'ctl00$ContentPlaceHolder1$ctl' + siteNum + '$ctl47$field_published_date': date,  # param, form yyyy-mm-dd
            'ctl00$ContentPlaceHolder1$ctl' + siteNum + '$ctl47$field_published_date$dateInput': fullDate,
            # param form dd month, yyyy (may have to be different from other date) convert from first type
            'ctl00_ContentPlaceHolder1_ctl' + siteNum + '_ctl47_field_published_date_dateInput_ClientState': publishedDateDict,
            # 2nd form
            'ctl00_ContentPlaceHolder1_ctl' + siteNum + '_ctl47_field_published_date_calendar_SD': '[]',
            'ctl00_ContentPlaceHolder1_ctl' + siteNum + '_ctl47_field_published_date_calendar_AD': dateList,
            'ctl00_ContentPlaceHolder1_ctl' + siteNum + '_ctl47_field_published_date_ClientState': '{"minDateStr":"1000-01-01-00-00-00","maxDateStr":"9999-12-31-00-00-00"}',
            'ctl00_ContentPlaceHolder1_ctl' + siteNum + '_ctl47_field_body_ctl00_dialogOpener_Window_ClientState': '',
            'ctl00_ContentPlaceHolder1_ctl' + siteNum + '_ctl47_field_body_ctl00_dialogOpener_ClientState': '',
            'ctl00$ContentPlaceHolder1$ctl' + siteNum + '$ctl47$field_body$ctl00': content,  # param
            'ctl00_ContentPlaceHolder1_ctl' + siteNum + '_ctl47_field_body_ctl00_ClientState': '',
            'ctl00$ContentPlaceHolder1$ctl' + siteNum + '$ctl47$field_pageLastModified_date': lastModifiedDate,
            'ctl00_ContentPlaceHolder1_ctl' + siteNum + '_ctl47_field_pageLastModified_date_dateInput_ClientState': modifiedDateDict,
            # extract likely needed, treat as other dict, bring in
            'ctl00_ContentPlaceHolder1_ctl' + siteNum + '_ctl47_field_pageLastModified_date_calendar_SD': '[]',
            'ctl00_ContentPlaceHolder1_ctl' + siteNum + '_ctl47_field_pageLastModified_date_calendar_AD': lastModifiedDateList,
            # might need to extract this due to last value
            'ctl00_ContentPlaceHolder1_ctl' + siteNum + '_ctl47_field_pageLastModified_date_ClientState': '{"minDateStr":"1000-01-01-00-00-00","maxDateStr":"9999-12-31-00-00-00"}',
            'ctl00_ContentPlaceHolder1_ctl' + siteNum + '_ctl47_RadWM_ClientState': '',
            'ctl00_ContentPlaceHolder1_ctl' + siteNum + '_ctl47_RadWindowLoadingImageManager_ClientState': '',
            'ctl00$ContentPlaceHolder1$ctl' + siteNum + '$hdfChangToPublish': '1',
            'ctl00$ContentPlaceHolder1$ctl' + siteNum + '$btnYes': 'Yes'}
    request = session.post(editUrl, data)
    request.raise_for_status()


def getSiteContent(url, newUrl=''):
    'Copies content from old site to new site'
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
    setVerticalFlag(BeautifulSoup(session.get(newUrl).content, 'html.parser'))
    localContentSite = session.get(newUrl + '/televox/LocalPortletLibrary.aspx')
    localContentHtml = localContentSite.content
    localContentSoup = BeautifulSoup(localContentHtml, 'html.parser')
    scripts = localContentSoup.find_all('script')
    for script in scripts:
        if 'nodeData' in script.text:
            rootIndex = script.text.find(
                'value')  # root will be the first result, next results will be folders, one for each on folder tree
            rootID = script.text[rootIndex + len('value') + 3:script.text.find('"', rootIndex + len('value') + 3)]
            parentIndex = script.text.find('value', rootIndex + len('value'))  # finds next folder
            collapseAnimationIndex = script.text.find('collapseAnimation', rootIndex + len('value'))
            if collapseAnimationIndex < parentIndex:
                try:
                    folderCreate = session.post(newUrl + 'TeleVox/WebServices/SharedContentService.asmx/CreateFolder',
                                                data={'parentId': rootID, 'folderName': 'Content'})
                    folderCreate.raise_for_status()
                except:
                    print 'Nowhere to save to, no content or portlets will be brought over.'
                    result.write('Nowhere to save to, no content or portlets will be brought over.\r\n')
                    return
    libraryUrl = newUrl + 'common/plugins/RadEditorAjax/SharedImageLibrary/SharedImageLibrary.aspx'
    libraryHtml = session.get(libraryUrl).content
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
            if newBlogUrl != '' and newBlogUrl != newLink.text[:newBlogUrlEnd]:
                print 'Error with blog url.'
                print 'Expected blog url: ' + newBlogUrl
                print 'Found blog url: ' + newLink.text[:newBlogUrlEnd]
            else:
                newBlogUrl = newLink.text[:newBlogUrlEnd]
        blogUrl = ''
    for link in linkList:
        if 'blog' in link.text:
            blogIndex = link.text.find('blog')
            blogUrlEnd = link.text.find('/', blogIndex) + 1  # 1st / after blog, inclusive
            if blogUrl != '' and blogUrl != link.text[:blogUrlEnd]:
                print 'Error with blog url.'
                print 'Expected blog url: ' + blogUrl
                print 'Found blog url: ' + link.text[:blogUrlEnd]
            else:
                blogUrl = link.text[:blogUrlEnd]
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
    queue = Queue.Queue(len(linkList) + len(blogList))
    lock = threading.Lock()
    threads = []
    maxThreadNum = 100
    if 100 >= len(linkList) + len(blogList):
        maxThreadNum = len(linkList) + len(blogList)

    for i in range(0, maxThreadNum):
        thread = contentThread(session, lock, queue, siteName, newSiteName, newBlogUrl, libraryHtml)
        thread.start()
        threads.append(thread)
    with lock:
        for subpage in linkList:
            if 'blog' not in subpage.text:
                queue.put(subpage.text)
        if blogUrl != '' and newBlogUrl != '':
            queue.put(blogUrl)
            for blogPost in blogList:
                queue.put(blogPost)
    while not queue.empty():
        pass

    global exit
    exit = True

    for thread in threads:
        thread.join()
    exit = False
    print url + ' is finished.'


def getMultipleSiteContent(txt):
    'Copies over metadata from multiple sites given a file with urls (must be spaces in between)'
    urls = []
    while (True):
        readUrl = readNextToken(txt)
        if readUrl == 'EOL':
            break
        else:
            urls.append(readUrl)
    for site in urls:
        getSiteContent(site)
