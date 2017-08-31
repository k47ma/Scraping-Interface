from HTMLParser import HTMLParser
import urllib2
import urllib
import cookielib


class metaParser(HTMLParser):
    'Extracts metadata from HTML'
    flagTitle = False
    flagDescription = False
    flagFirstDescription = True
    title = ""
    description = ""

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.flagTitle = True

        if tag == 'meta':
            for name, value in attrs:
                if name == 'name' and value == 'description' and self.flagFirstDescription:
                    self.flagFirstDescription = False
                    self.flagDescription = True
                if name == 'content' and self.flagDescription:
                    self.description = value

    def handle_endtag(self, tag):
        if tag == 'title':
            self.flagTitle = False

        if tag == 'meta':
            self.flagDescription = False

    def handle_data(self, data):
        if self.flagTitle:
            self.title = data


class sitemapParser(HTMLParser):
    'Extracts urls from a the HTML of a sitemap page'
    linkList = []
    flagCurrentTag = False

    def handle_starttag(self, tag, attrs):
        if tag == 'loc':
            self.flagCurrentTag = True

    def handle_endtag(self, tag):
        if tag == 'loc':
            self.flagCurrentTag = False

    def handle_data(self, data):
        if self.flagCurrentTag:
            self.linkList.append(data)


class viewStateParser(HTMLParser):
    'Finds the massive value of viewState'
    viewState = ''
    flagInput = False
    flagCurrentInput = False

    def handle_starttag(self, tag, attrs):
        if tag == 'input':
            self.flagInput = True
            for name, value in attrs:
                if name == 'name' and value == '__VIEWSTATE':
                    self.flagCurrentInput = True
                if self.flagCurrentInput and name == 'value':
                    self.viewState = value
                    self.flagCurrentInput = False

    def handle_endtag(self, tag):
        if tag == 'input':
            self.flagInput = False


def getSiteMeta(url):
    'Takes all the metadata from a website'
    siteParser = sitemapParser()
    cj = cookielib.CookieJar()
    metaList = []
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    try:
        sitemap = urllib2.urlopen(url + 'pagesitemap.xml')
    except:
        sitemap = urllib2.urlopen(url + 'sitemap.xml')
        viewParser = viewStateParser()
        loginSite = opener.open(url)
        loginHtml = loginSite.read()
        viewParser.feed(loginHtml)
        viewState = viewParser.viewState
        viewParser.close()
        values = {'ctl00_RadStyleSheetManager1_TSSM': '',
                  'ctl00_ScriptManager1_TSM': '',
                  '__EVENTTARGET': '',
                  '__EVENTARGUMENT': '',
                  '__VIEWSTATE': viewState,
                  '__VIEWSTATEGENERATOR': '6BCC8CC6',
                  'ctl00$ContentPlaceHolder1$txtUsername': 'evan.brearley',
                  'ctl00$ContentPlaceHolder1$txtPassword': 'Welcome1234',
                  'ctl00$ContentPlaceHolder1$btnLogin': 'Login'}
        data = urllib.urlencode(values)
        request = urllib2.Request(url + 'gateway/Login.aspx?ReturnUrl=%2f', data)
        opener.open(request)
    sitemapHtml = sitemap.read()
    siteParser.feed(sitemapHtml)
    for subpage in siteParser.linkList:
        metaDataParser = metaParser()
        site = opener.open(subpage)
        metaHtml = site.read()
        metaDataParser.feed(metaHtml)
        metaTuple = (metaDataParser.title, metaDataParser.description)
        metaList.append(metaTuple)
        metaDataParser.close()
    siteParser.close()
    for i in metaList:
        print i[0]
        print i[1]


getSiteMeta('http://owlortho.televox.west.com/')
