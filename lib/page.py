import os
import threading
import Queue
import requests
from bs4 import BeautifulSoup
from config import settings
from QA_util import create_path

verticalSite = False
tellPos = 0
create_path()
result = open('result\\pageResult.txt', 'w')  # garbage collection will close


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
                tellPos = 0  # returning this value indicates end of file, reset tellPos for next file, READING MULTIPLE FILES UNTESTED, function has only been called once per run so far
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


class listThread(threading.Thread):
    def __init__(self, session, lock, newMenu, siteName, newSiteName, blogUrl, returnList):
        threading.Thread.__init__(self)
        self.session = session
        self.lock = lock
        self.newMenu = newMenu
        self.siteName = siteName
        self.newSiteName = newSiteName
        self.blogUrl = blogUrl
        self.returnList = returnList

    def run(self):
        for subpage in self.newMenu:
            if 'blog' in subpage:
                copyPage(self.session, subpage, self.siteName, self.newSiteName, 'blogpage')
            else:
                copyPage(self.session, subpage, self.siteName, self.newSiteName)
        with self.lock:
            self.returnList.append('done')


exit = False


class pageThread(threading.Thread):
    def __init__(self, session, lock, queue, siteName, newSiteName):
        threading.Thread.__init__(self)
        self.session = session
        self.lock = lock
        self.queue = queue
        self.siteName = siteName
        self.newSiteName = newSiteName

    def run(self):
        global exit
        while not exit:
            with self.lock:
                if not self.queue.empty():
                    url = self.queue.get()
                    copyPage(self.session, url, self.siteName, self.newSiteName)


def copyPage(session, url, siteName, newSiteName, pageType=''):
    friendlyIndex = url.find('/', url.find(siteName)) + 1  # first index after first slash after sitename
    if 'main' in url or 'home' in url:
        return
    if 'http' in url and siteName not in url:
        return
    if 'blog' in url and pageType != 'blogpage':
        return
    if 'https' in url:
        newUrl = 'https://' + newSiteName + '.televox.west.com/' + url[friendlyIndex:]
    else:
        newUrl = 'http://' + newSiteName + '.televox.west.com/' + url[friendlyIndex:]
    try:
        if newUrl[len(newUrl) - len('blog'):] != 'blog':
            pageCheck = session.get(newUrl)
            pageCheck.raise_for_status()
        else:
            pageCheck = session.get(
                newUrl[:len(newUrl) - len('blog')] + 'our-blog')  # this accounts for the switch to our blog
            pageCheck.raise_for_status()
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 404:
            parentEnd = url.rfind('/', 0, len(url) - 1)
            if parentEnd == -1:
                parentEnd = friendlyIndex - 1
            parentUrl = 'http://' + newSiteName + '.televox.west.com/' + url[friendlyIndex:parentEnd]
            if parentUrl == 'http://' + newSiteName + '.televox.west.com/':
                parentIsHome = True
            else:
                parentIsHome = False
            name = url[parentEnd + 1:]
            try:
                site = session.get(url)
                site.raise_for_status()
                html = site.content
                soup = BeautifulSoup(html, 'html.parser')
                title = soup.find('h1').text  # assuming title is a h1
            except:
                title = name.replace('-', ' ').title()
            if parentUrl[len(parentUrl) - 4:].replace('/', '') == 'blog':
                parentUrl = parentUrl[:len(parentUrl) - 4] + 'our-blog'
            if pageType == 'blogpage':
                addPage(session, parentUrl, title, name, pageType='blogpage', parentIsHomepage=parentIsHome)
            else:
                addPage(session, parentUrl, title, name, parentIsHomepage=parentIsHome)


def modifyBlogPost(session, url, content='', title='', summary='', fullDate=''):
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
    editSite.raise_for_status()
    editHtml = editSite.content
    editSoup = BeautifulSoup(editHtml, 'html.parser')
    viewState = editSoup.find('input', {'id': '__VIEWSTATE'})['value']
    generator = editSoup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value']
    global verticalSite
    if verticalSite:
        siteNum = '02'
    else:
        siteNum = '07'
    if title == '':
        titleTag = editSoup.find('input', {'name': 'ctl00$ContentPlaceHolder1$ctl' + siteNum + '$ctl47$field_title'})
        if titleTag.has_attr('value'):
            title = titleTag['value']
        else:
            title = ''
    if fullDate == '':
        fullDateTag = editSoup.find('input', {
            'name': 'ctl00$ContentPlaceHolder1$ctl' + siteNum + '$ctl47$field_published_date$dateInput'})
        if fullDateTag.has_attr('value'):
            fullDate = fullDateTag['value']
        else:
            fullDate = ''
    else:
        monthDict = {'January': '01', 'Jan': '01', 'February': '02', 'Feb': '02', 'March': '03', 'Mar': '03',
                     'April': '04', 'Apr': '04', 'May': '05', 'June': '06', 'Jun': '06',
                     'July': '07', 'Jul': '07', 'August': '08', 'Aug': '08', 'September': '09', 'Sep': '09',
                     'October': '10', 'Oct': '10', 'November': '11', 'Nov': '11', 'December': '12', 'Dec': '12'}
        day = fullDate[:2]
        year = fullDate[len(fullDate) - 4:]
        monthWord = fullDate[3: fullDate.find(' ', 3)].replace('.', '')
        month = monthDict[monthWord]
        date = year + '-' + month + '-' + day
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
    if date == '':
        dateTag = editSoup.find('input',
                                {'name': 'ctl00$ContentPlaceHolder1$ctl' + siteNum + '$ctl47$field_published_date'})
        if dateTag.has_attr('value'):
            date = dateTag['value']
        else:
            date = ''
    dateList = editSoup.find('input', {
        'name': 'ctl00_ContentPlaceHolder1_ctl' + siteNum + '_ctl47_field_published_date_calendar_AD'})['value']
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
            'ctl00$ContentPlaceHolder1$ctl' + siteNum + '$ibPublishBottom': 'Publish'}
    request = session.post(editUrl, data)
    request.raise_for_status()


def login(url):
    username = settings["USER_NAME"]
    password = settings["PASSWORD"]
    index = url.find('.com/') + 5
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
    request = session.post(urlStart + 'gateway/Login.aspx?ReturnUrl=%2f', values)
    request.raise_for_status()
    return session


def addPage(session, parentUrl, title, pageName, pageType='content', redirectUrl='', parentIsHomepage=False):
    username = settings["USER_NAME"]
    'Adds either a content space page or an external link page given a logged in session'
    try:
        parentSite = session.get(parentUrl)
        parentSite.raise_for_status()
    except:
        result.write(parentUrl + ' failed to open, ' + pageName + ' not added.\r\n')
        return
    if pageName == 'blog':
        name = 'our-blog'
    else:
        name = pageName
    print 'Adding: ' + parentUrl + '/' + name
    parentHtml = parentSite.content
    parentSoup = BeautifulSoup(parentHtml, 'html.parser')
    index = parentUrl.find('.com/') + 4
    urlStart = parentUrl[:index]
    if redirectUrl == '':
        redirectUrl = parentUrl[len(urlStart):]
    cmsUrlLoc = parentSoup.find('form', {'method': 'post'})
    if cmsUrlLoc == None:
        parentSite = session.get(parentUrl)
        parentSite.raise_for_status()
        parentHtml = parentSite.content
        parentSoup = BeautifulSoup(parentHtml, 'html.parser')
        cmsUrlLoc = parentSoup.find('form', {'method': 'post'})
    cmsUrl = cmsUrlLoc['action']
    parentIdStart = cmsUrl.find('pageId=') + len('pageId=')
    parentId = cmsUrl[parentIdStart:]
    contentUrl = urlStart + '/cms/' + cmsUrl + '&action=addTypedPage&parentId=' + parentId + '&pageType=Content+Space+Page'
    externalLinkUrl = urlStart + '/cms/' + cmsUrl + '&action=addextlinkpage&parentId=' + parentId
    blogPageUrl = urlStart + '/cms/' + cmsUrl + '&action=addTypedPage&parentId=' + parentId + '&pageType=News%2fBlog+Page'
    blogPostUrl = urlStart + '/cms/' + cmsUrl + '&action=addTypedPage&parentId=' + parentId + '&pageType=News%2fBlog+Content+Page'
    pageTypeUrl = {'content': contentUrl, 'external': externalLinkUrl, 'blogpage': blogPageUrl, 'blogpost': blogPostUrl}
    try:
        formUrl = pageTypeUrl[pageType]
    except:
        result.write(
            'Invalid page type, only content, blogpage, blogpost and external are accepted inputs for the pageType.\r\n')
        result.write('Page addition failed for: ' + parentUrl + ' with ' + title + ' and ' + name + '\r\n')
        return
    formSite = session.get(formUrl)
    formSite.raise_for_status()
    formHtml = formSite.content
    formSoup = BeautifulSoup(formHtml, 'html.parser')
    viewState = formSoup.find('input', {'id': '__VIEWSTATE'})['value']
    generator = formSoup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value']
    global verticalSite
    if verticalSite:
        siteNum1 = '01'
        siteNum2 = '10'
    else:
        siteNum2 = '08'
        if parentIsHomepage:
            siteNum1 = '03'
        else:
            siteNum1 = '06'
    try:
        ownerID = formSoup.find('input', {'id': 'ctl00_ContentPlaceHolder1_ctl' + siteNum1 + '_hfOwnerId'})['value']
    except:
        print 'If there is a gallery in the sidebar of level 1s, delete and try again.'
        result.write('If there is a gallery in the sidebar of level 1s, delete and try again.\r\n')
    if pageType == 'external':
        data = {'ctl00_RadStyleSheetManager1_TSSM': '',
                'ctl00_ScriptManager1_TSM': '',
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__LASTFOCUS': '',
                '__VIEWSTATE': viewState,
                '__VIEWSTATEGENERATOR': generator,
                'ctl00_ContentPlaceHolder1_RadWindowManagerLoadingContentTree_ClientState': '',
                'ctl00_ContentPlaceHolder1_RadWindowLoadingContentTree_ClientState': '',
                'ctl00_ContentPlaceHolder1_RadWindowPermissionControl_ClientState': '',
                'ctl00_ContentPlaceHolder1_ctl00_RadWND_ClientState': '',
                'ctl00_ContentPlaceHolder1_ctl01_radmenu_ClientState': '',
                'ctl00$ContentPlaceHolder1$ctl' + siteNum1 + '$txtTitle': title.strip(),
                'ctl00$ContentPlaceHolder1$ctl' + siteNum1 + '$txtCanonicalName': name,
                'ctl00$ContentPlaceHolder1$ctl' + siteNum1 + '$ddlProtocol': '',
                'ctl00$ContentPlaceHolder1$ctl' + siteNum1 + '$txtUrl': redirectUrl,
                'ctl00$ContentPlaceHolder1$ctl' + siteNum1 + '$rblTypes': 'ExternalUrl',
                'ctl00$ContentPlaceHolder1$ctl' + siteNum1 + '$hiddenObjectId': '',
                'ctl00$ContentPlaceHolder1$ctl' + siteNum1 + '$hiddenObjectName': '',
                'ctl00$ContentPlaceHolder1$ctl' + siteNum1 + '$rblNewPageWindow': 'Open the external link page in existing window',
                'ctl00$ContentPlaceHolder1$ctl' + siteNum1 + '$ctl' + siteNum2 + '$ddlCategory': '',
                'ctl00$ContentPlaceHolder1$ctl' + siteNum1 + '$ctl' + siteNum2 + '$txtCategory': '',
                'ctl00$ContentPlaceHolder1$ctl' + siteNum1 + '$ctl' + siteNum2 + '$txtFeaturedImage': '',
                'ctl00_ContentPlaceHolder1_ctl' + siteNum1 + '_ctl' + siteNum2 + '_RadWM_ClientState': '',
                'ctl00_ContentPlaceHolder1_ctl' + siteNum1 + '_ctl' + siteNum2 + '_ExplorerWindow_ClientState': '',
                'ctl00_ContentPlaceHolder1_ctl' + siteNum1 + '_ctl' + siteNum2 + '_RadWindowLoadingImageManager_ClientState': '',
                'ctl00$ContentPlaceHolder1$ctl' + siteNum1 + '$btnSubmit': 'Create Page',
                'ctl00_ContentPlaceHolder1_ctl' + siteNum1 + '_ExplorerWindow_ClientState': '',
                'ctl00_ContentPlaceHolder1_ctl' + siteNum1 + '_RadWindowLoadingFileManager_ClientState': ''}
    else:
        data = {'ctl00_RadStyleSheetManager1_TSSM': '',
                'ctl00_ScriptManager1_TSM': '',
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': viewState,
                '__VIEWSTATEGENERATOR': generator,
                'ctl00_ContentPlaceHolder1_RadWindowManagerLoadingContentTree_ClientState': '',
                'ctl00_ContentPlaceHolder1_RadWindowLoadingContentTree_ClientState': '',
                # IS l03 normally, see external
                'ctl00_ContentPlaceHolder1_RadWindowPermissionControl_ClientState': '',
                'ctl00_ContentPlaceHolder1_ctl00_RadWND_ClientState': '',
                'ctl00_ContentPlaceHolder1_ctl01_radmenu_ClientState': '',
                'ctl00$ContentPlaceHolder1$ctl' + siteNum1 + '$txtTitle': title.strip(),
                'ctl00$ContentPlaceHolder1$ctl' + siteNum1 + '$txtCanonicalName': name,
                'ctl00$ContentPlaceHolder1$ctl' + siteNum1 + '$txtOwner': username,
                'ctl00$ContentPlaceHolder1$ctl' + siteNum1 + '$hfOwnerId': ownerID,
                'ctl00$ContentPlaceHolder1$ctl' + siteNum1 + '$hfIconName': '',
                'ctl00$ContentPlaceHolder1$ctl' + siteNum1 + '$ctl' + siteNum2 + '$ddlCategory': '',
                'ctl00$ContentPlaceHolder1$ctl' + siteNum1 + '$ctl' + siteNum2 + '$txtCategory': '',
                'ctl00$ContentPlaceHolder1$ctl' + siteNum1 + '$ctl' + siteNum2 + '$txtFeaturedImage': '',
                'ctl00_ContentPlaceHolder1_ctl' + siteNum1 + '_ctl' + siteNum2 + '_RadWM_ClientState': '',
                'ctl00_ContentPlaceHolder1_ctl' + siteNum1 + '_ctl' + siteNum2 + '_ExplorerWindow_ClientState': '',
                'ctl00_ContentPlaceHolder1_ctl' + siteNum1 + '_ctl' + siteNum2 + '_RadWindowLoadingImageManager_ClientState': '',
                'ctl00$ContentPlaceHolder1$ctl' + siteNum1 + '$btnSubmit': 'Create Page'}
    try:
        newPageReq = session.post(formUrl, data)
        newPageReq.raise_for_status()
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 500:
            print err.response
            result.write(
                'Internal Server Error, try running the code again, if it fails the form submission is faulty.\r\n')
            result.write('Page addition failed for: ' + parentUrl + ' with ' + title + ' and ' + name + '\r\n')
        elif err.response.status_code == 302:
            pass
        else:
            print err.response
            result.write('Page addition failed for: ' + parentUrl + ' with ' + title + ' and ' + name + '\r\n')


def createSitePages(url, newUrl=''):
    'Adds all pages to a site'
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
    session = login(newUrl)
    setVerticalFlag(BeautifulSoup(session.get(newUrl).content, 'html.parser'))
    sitemap = session.get(url + 'pagesitemap.xml')
    sitemapHtml = sitemap.content
    sitemapSoup = BeautifulSoup(sitemapHtml, 'html.parser')
    linkList = sitemapSoup.find_all('loc')
    newMap = session.get(newUrl + 'sitemap.xml')
    newHtml = newMap.content
    newMapSoup = BeautifulSoup(newHtml, 'html.parser')
    newLinks = newMapSoup.find_all('loc')
    newBlogUrl = ''
    blogUrl = ''
    for link in linkList:
        if 'blog' in link.text:
            blogIndex = link.text.find('blog')
            blogUrlEnd = link.text.find('/', blogIndex) + 1  # 1st / after blog, inclusive
            if blogUrl.strip() != '' and blogUrl != link.text[:blogUrlEnd]:
                result.write('Error with blog url.\r\n')
                result.write('Expected blog url: ' + blogUrl + '\r\n')
                result.write('Found blog url: ' + link.text[:blogUrlEnd] + '\r\n')
            else:
                if link.text[:blogUrlEnd].strip() != '':
                    blogUrl = link.text[:blogUrlEnd]
    blogFriendlyStart = blogUrl.find('/', blogUrl.find(siteName)) + 1
    if blogUrl[blogUrl.rfind('/', 0, len(blogUrl) - 1):].replace('/', '') == 'blog':
        newBlogUrl = 'http://' + newSiteName + '.televox.west.com/' + blogUrl[blogFriendlyStart:blogUrl.rfind('/', 0,
                                                                                                              len(
                                                                                                                  blogUrl) - 1)] + '/our-blog/'
    else:
        newBlogUrl = 'http://' + newSiteName + '.televox.west.com/' + blogUrl[
                                                                      blogFriendlyStart:]  # same method as generating newUrl for normal pages
    blogList = []
    blogTitles = []
    summaryList = []
    dateList = []
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
                blogTitles.append(a.text)
            paragraphs = li.find_all('p')
            date = paragraphs[0].text[:paragraphs[0].text.find('|')].strip()
            if '|' in paragraphs[0].text:
                dateList.append(date)
            else:
                dateList.append('')
            if len(paragraphs) > 1:
                summaryList.append(paragraphs[len(paragraphs) - 1].text)
            else:
                summaryList.append('')
    linkTextList = []
    for link in linkList:
        linkTextList.append(link.text)
    homePage = session.get(url)
    homeHtml = homePage.content
    homeSoup = BeautifulSoup(homeHtml, 'html.parser')
    navBar = homeSoup.find('nav', {'id': 'primary-navigation'})
    menuLinks = navBar.find_all('a')
    listList = []
    subpageList = []
    topLevelList = []
    currentTopLevelUrl = ''
    for menuLink in menuLinks:
        if 'File Library' in menuLink['href']:
            continue
        href = menuLink['href']
        if siteName not in href and 'http' in href:
            continue
        if siteName not in href:
            topLevelEnd = href.find('/', 1)  # ignore first character
            if topLevelEnd == -1:
                topLevelEnd = len(href)
            topLevelFriendly = href[1:topLevelEnd]
            topLevelUrl = url + topLevelFriendly
            fullUrl = url + href[1:]  # get rid of the slash at the front
        else:
            topLevelFriendlyStart = href.find(siteName) + len(siteName) + len('.com')
            topLevelEnd = href.find('/', topLevelFriendlyStart + 1)
            if topLevelEnd == -1:
                topLevelEnd = len(href)
            topLevelUrl = href[:topLevelEnd]
            fullUrl = href
        if currentTopLevelUrl == '':
            currentTopLevelUrl = topLevelUrl
            topLevelList.append(topLevelUrl)
            if topLevelUrl in linkTextList:
                linkTextList.remove(topLevelUrl)
        elif currentTopLevelUrl != topLevelUrl:
            # now in a different drop down
            topLevelList.append(topLevelUrl)
            listList.append(list(subpageList))  # append a copy of the list
            subpageList[:] = []
            currentTopLevelUrl = topLevelUrl
        if fullUrl not in subpageList:
            subpageList.append(fullUrl)
        if fullUrl in linkTextList:
            linkTextList.remove(fullUrl)
    listList.append(subpageList)  # there will be an extra list leftover as they are only added when a new one begins
    for topLevelPage in topLevelList:
        print topLevelPage
        if 'main' in topLevelPage or 'home' in topLevelPage or topLevelPage == newUrl:
            continue
        topLevelFriendly = topLevelPage[len(url):]
        newTopLevelPage = newUrl + topLevelFriendly
        try:
            pageTestReq = session.get(newTopLevelPage)
            pageTestReq.raise_for_status()
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 404:
                name = topLevelFriendly.replace('/', '')  # these pages should be level 1s
                title = name.replace('-', ' ').title()  # assuming no special characters in top level pages, FASTER
                parentUrl = newUrl
                if 'blog' in name:  # assuming this would have to be the blog page then
                    addPage(session, parentUrl, title, name, 'blogpage', parentIsHomepage=True)
                else:
                    addPage(session, parentUrl, title, name, parentIsHomepage=True)
    # add subpages and miscellaneous pages, thread on each list in listList, looping through them in order to create pages in order then add all other pages async, then blog posts in a loop
    topThreads = []
    returnList = []
    lock = threading.Lock()
    for newMenu in listList:
        print newMenu
        topThread = listThread(session, lock, newMenu, siteName, newSiteName, blogUrl,
                               returnList)
        topThread.start()
        topThreads.append(topThread)
    while len(returnList) < len(topLevelList):
        pass
    for thread in topThreads:
        thread.join()
    # menus should be complete at this point, add miscellaneous pages, then blog posts, main blog page should already be made
    queue = Queue.Queue()
    miscThreads = []
    threadNum = min(50, len(linkTextList))
    for i in range(0, threadNum):
        miscThread = pageThread(session, lock, queue, siteName, newSiteName)
        miscThread.start()
        miscThreads.append(miscThread)
    with lock:
        for link in linkTextList:
            queue.put(link)
    while not queue.empty():
        pass
    global exit
    exit = True
    for thread in miscThreads:
        thread.join()
    blogNum = 0
    for blogPost in blogList:
        lastSlash = blogPost.rfind('/', 0, len(blogPost) - 1) + 1  # index after last slash
        if len(blogPost[lastSlash:]) > 50:
            newBlogPost = newBlogUrl + blogPost[lastSlash:lastSlash + 50]
        else:
            newBlogPost = newBlogUrl + blogPost[lastSlash:]
        try:
            blogPageReq = session.get(newBlogPost)
            blogPageReq.raise_for_status()
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 404:
                parentUrl = newBlogUrl
                name = newBlogPost[len(newBlogUrl):]
                oldPostSite = session.get(blogPost)
                oldPostHtml = oldPostSite.content
                oldPostSoup = BeautifulSoup(oldPostHtml, 'html.parser')
                article = oldPostSoup.find('article')
                title = article.find('h1').text  # assuming title will always be a h1 on old sites
                addPage(session, parentUrl, title, name, 'blogpost')
                print newBlogPost
                try:
                    modifyBlogPost(session, newBlogPost, '', blogTitles[blogNum], summaryList[blogNum],
                                   dateList[blogNum])
                except:
                    print newBlogPost + ' failed'
                    result.write(newBlogPost + ' failed.\r\n')
        blogNum += 1
    print url + ' is finished.'


def makeMultipleSitesPages(txt):
    'Copies over metadata from multiple sites'
    urls = []
    while (True):
        readUrl = readNextToken(txt)
        if readUrl == 'EOL':
            break
        else:
            urls.append(readUrl)
    for site in urls:
        global exit
        exit = False
        result.write(site)
        createSitePages(site)
