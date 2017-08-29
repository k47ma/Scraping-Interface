import requests
import os
import sys
import time
from config import settings
import urllib
from bs4 import BeautifulSoup

# testing method to ignore images in forms and galleries
# testing text output of errors
# testing deleting files as after they are uploaded
# testing new commands for input in the text file
# testing support for sites that change siteName, this is already tested a bit, but bugs still could emerge

result = open('result\\contentResult.txt',
              'w')  # lazy, easier than passing it through all functions, will correct later, I want this file open the entire time; garbage collection will close it for now, addign with for wach write will come later
tellPos = 0  # need this to remain constant across multiple calls of the function, resetting only at the end of the file


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
                newFile.close()  # done with the file
                return 'EOF'
            else:
                flag = True
                if str.strip() != '':
                    return str.strip()


def login(url):
    username = settings["USER_NAME"]
    password = settings["PASSWORD"]
    session = requests.Session()
    index = url.find('.com/') + 5
    urlStart = url[:index]
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
    session.post(urlStart + 'gateway/Login.aspx?ReturnUrl=%2f', data=values)
    return session


def uploadImages(session, url, images, siteName, newSiteName, rootFolderID):
    newUrl = 'http://' + newSiteName + '.televox.west.com/'
    friendlyIndex = url.find('/', url.find(siteName))
    folderName = url[friendlyIndex + 1:].replace('/', ' ')
    newFolderUrl = newUrl + 'TeleVox/WebServices/SharedImageService.asmx/CreateFolder'
    folderData = {'folderName': folderName,
                  'parentId': rootFolderID}
    resp = session.post(newFolderUrl, data=folderData)
    updatedFolders = getImageLibrary(session, newUrl)
    newestFile = str(max(updatedFolders))
    for image in images:
        try:
            with open(image, 'rb') as f:
                files = {'file': (image, f, 'image/' + image[image.find('.') + 1:])}
                data = {'name': image,
                        'chunk': '0',
                        'chunks': '1',
                        'parentId': newestFile,
                        'objectType': 'shared_image',
                        'filters[mime_types][][title]': 'Image types',
                        'filters[mime_types][][extensions]': 'bmp,cal,cgm,cmx,dsf,dwg,dxf,fif,g3f,gif,ico,ief,jpe,jpeg,jpg,mil,pbm,pcd,pgm,pict,png,pnm,ppm,ras,rgb,svf,svg,tif,tiff,wi,xbm,xpm,xwd',
                        'mxupload': '100',
                        'objectid': '0',
                        'isRevision': 'false'}
                request = session.post(newUrl + 'Common/controls/multipleFileUpload/plupload/fileUploadHandler',
                                       data=data, files=files)  # urlstart should include / after .com
        except:
            result.write('Image upload failed for: ' + url + '\r\n')
    files = list(set(
        images))  # casting to set removes duplicates, then back to list for loop, no attempts to delete deleted files
    for image in files:
        try:
            os.remove(image)  # delete the files after they have been uploaded or failed to upload
        except OSError as err:
            result.write(str(err) + '\r\n')


def getImageLibrary(session, urlStart):
    'Returns a list of folder IDs, which can be used to find min (root) and max ID (newest)'
    libraryUrl = urlStart + 'common/plugins/RadEditorAjax/SharedImageLibrary/SharedImageLibrary.aspx'
    libraryHtml = session.get(libraryUrl).content
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
    response = session.post(libraryUrl, data=data)
    content = response.content
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
    return folders


def download(src, name):
    downloadedFile = urllib.urlretrieve(src, name, progressReporter)


def progressReporter(blockNum, blockSize, totalSize):
    percent = int(blockNum * blockSize / totalSize * 100)
    sys.stdout.write('\r' + 'Download: ' + str(percent) + '%')
    sys.stdout.flush()


def migratePageImages(session, url, siteName, newSiteName, rootFolderID):
    try:
        site = session.get(url)
        site.raise_for_status()
    except:
        result.write('Invalid url? ' + url + '\r\n')
        return
    html = site.content
    soup = BeautifulSoup(html, 'html.parser')
    contentDiv = soup.find('div', {'id': 'content'})
    try:
        images = contentDiv.find_all('img')
    except:
        return
    downloadList = []
    imageList = []
    for image in images:
        if image.has_attr('src'):
            if siteName in image['src'] or 'televox' in image['src'] or image['src'][:1] == '/':
                downloadList.append(image['src'])
    forms = soup.find_all('div', {'class': 'CLFormContainer'})
    for form in forms:
        formImages = form.find_all('img')
        for image in formImages:
            if image.has_attr('src'):
                if siteName in image['src'] or 'televox' in image['src'] or image['src'][:1] == '/':
                    downloadList.remove(image['src'])
    galleries = soup.find_all('div', {'class': 'slide-show'})
    for gallery in galleries:
        galleryImages = gallery.find_all('img')
        for image in galleryImages:
            if image.has_attr('src'):
                if siteName in image['src'] or 'televox' in image['src'] or image['src'][:1] == '/':
                    downloadList.remove(image['src'])
    for link in downloadList:
        if link[:1] == '/':
            link = url + link[1:]
        lastSlash = link.rfind('/')
        name = link[lastSlash + 1:]
        imageList.append(name)
        try:
            download(link, name)
        except:
            result.write('An image download failed at: ' + url + '\r\n')
    if len(imageList) > 0:
        uploadImages(session, url, imageList, siteName, newSiteName, rootFolderID)


def migrateSiteImages(url, newUrl=''):
    consent = raw_input('Are you sure you want to do the images for ' + url + '? If not, enter lowercase n\n')
    if consent == 'n':
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
        newNameStart = newUrl.find('//') + 1  # new sites have no www
        newNameEnd = newUrl.find('.', newNameStart + 1)
        newSiteName = newUrl[newNameStart + 1: newNameEnd]
        if 'tv01stg' in newUrl:  # for testing on staging sites
            newSiteName += '.tv01stg'
    session = login(newUrl)
    sitemap = session.get(url + 'pagesitemap.xml')
    sitemapHtml = sitemap.content
    sitemapSoup = BeautifulSoup(sitemapHtml, 'html.parser')
    linkList = sitemapSoup.find_all('loc')
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
            a = li.find('a')  # only gets first in clearfix, ASSUMING CLEARFIX CLASS PRESENT
            if a != None:
                blogList.append(a['href'])
    originalFolders = getImageLibrary(session, newUrl)
    rootFolderID = str(min(originalFolders))
    for subpage in linkList:
        if 'blog' not in subpage.text:
            migratePageImages(session, subpage.text, siteName, newSiteName, rootFolderID)
    if blogUrl != '':
        # migratePageImages(session, blogUrl, siteName, rootFolderID)
        for blogPost in blogList:
            migratePageImages(session, blogPost, siteName, newSiteName, rootFolderID)


def migrateMultipleSiteImages(txt):
    'Copies over metadata from multiple sites given a file with urls (must be spaces in between)'
    urls = []
    doubleList = []
    while (True):
        readUrl = readNextToken(txt)
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
        migrateSiteImages(site)
    for (oldUrl, newUrl) in doubleList:
        result.write(oldUrl + '\r\n')
        migrateSiteImages(oldUrl, newUrl)
