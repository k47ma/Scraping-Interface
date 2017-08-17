import re
from bs4 import Comment, Doctype, ProcessingInstruction

# module for storing key values


settings = {

    # username and password for login
    "USER_NAME": "",
    "PASSWORD": "",

    # path to the chromedriver
    "EXECUTABLE_PATH": "chromedriver\chromedriver.exe",

    # size of the thread pool
    "THREADPOOL_SIZE": 5,

    # when getting soup
    "GET_OLD_SOUP_IGNORE": [(['script', 'style', 'iframe', 'noscript'], {}),
                            ('div', {'text': re.compile("Provided for")}),
                            ('div', {'id': re.compile("dear_doctor_video_widget_video_container|google_translate_element")}),
                            ('div', {'class': re.compile("^(telerik_paste_container|single-map)$")}),
                            ('object', {'id': re.compile("kaltura_player")}),
                            ('', {'class': "offScreen"})],

    "GET_NEW_SOUP_IGNORE": [(['script', 'style', 'iframe', 'noscript'], {}),
                            ('div', {'text': re.compile("Provided for")}),
                            ('div', {'id': re.compile("dear_doctor_video_widget_video_container|google_translate_element")}),
                            ('div', {'class': re.compile("^(telerik_paste_container|single-map)$")}),
                            ('object', {'id': re.compile("kaltura_player")}),
                            ('', {'class': "offScreen"})],

    # when getting content from normal pages
    "GET_OLD_CONTENT_IGNORE": [(['style', 'script', 'iframe', 'title'], {}),
                               ('h1', {'class': "PageTitle"}),
                               ('', {'string': lambda str: isinstance(str, (Comment, Doctype, ProcessingInstruction))}),
                               ('div', {'class': re.compile("^(video-player|iapps-form|slide-show|map|secureform)$")}),
                               ('div', {'class': re.compile("form-container")}),
                               ('div', {'id': re.compile("^(review-widget-container|banner|sharing|footer)$")}),
                               ('', {'style': re.compile("display:( )*none")}),
                               ('nav', {'id': "section-navigation"}),
                               ('', {'itemprop': "review"}),
                               ('footer', {'id': "footer"})],

    "GET_NEW_CONTENT_IGNORE": [(['style', 'script', 'iframe', 'title'], {}),
                               ('h1', {'class': "PageTitle"}),
                               ('', {'string': lambda str: isinstance(str, (Comment, Doctype, ProcessingInstruction))}),
                               ('', {'id': re.compile("divView")}),
                               ('div', {'class': re.compile(
                                   "^(video-player|ptl_portlet_CustomForm|photoGallery|sidenav-slide)$")}),
                               ('div',
                                {'id': re.compile("^(review-widget-container|banner|sharing|footer|D3cpWidget)$")}),
                               ('', {'style': re.compile("display:( )*none")}),
                               ('', {'class': re.compile("WebWidget")}),
                               ('', {'itemprop': "review"}),
                               ('footer', {'id': "footer"})],

    # when getting content from blog pages
    "GET_BLOG_CONTENT_IGNORE": [(['style', 'script', 'iframe'], {}),
                                ('', {'string':
                                          lambda str: isinstance(str, (Comment, Doctype, ProcessingInstruction))}),
                                ('div', {'class': re.compile("^(video-player|iapps-form)$")}),
                                ('div', {'id': "review-widget-container"}),
                                ('', {'style': re.compile("display:( )*none")})],

    # when getting content for homepage
    "GET_HOMEPAGE_CONTENT_IGNORE": [(['style', 'script', 'iframe', 'title'], {}),
                                    ('', {'string': lambda str: isinstance(str,
                                                                           (Comment, Doctype, ProcessingInstruction))}),
                                    ('div', {'class': re.compile(
                                        "^(video-player|iapps-form|slide-show|map|offScreen|hours|locations)$")}),
                                    ('ul', {'class': re.compile("^(locations)$")}),
                                    ('div', {'id': re.compile("^(review-widget-container|google_translate_element|tel-fb)$")}),
                                    ('div', {'id': re.compile("fwXmlPhotoTheme")}),
                                    ('', {'style': re.compile("display:( )*none")}),
                                    ('', {'class': re.compile("form-container")}),
                                    ('html', {'id': "facebook"}),
                                    ('aside', {'class': re.compile("twitter")})],

    # when comparing links
    "COMPARE_OLD_LINK_IGNORE": [('a', {'href': re.compile("deardoctor|contentselector|javascript|fast\.wistia\.net")})],

    "COMPARE_NEW_LINK_IGNORE": [('a', {'href': re.compile("deardoctor|contentselector|javascript|fast\.wistia\.net")})],

    # when comparing images
    "COMPARE_OLD_IMAGE_IGNORE": [('img', {'width': re.compile("^(0|0px)$")}),
                                 ('img', {'height': re.compile("^(0|0px)$")}),
                                 ('img', {'src': re.compile("payment_calculator|demandforce_logo|fbcdn")}),
                                 ('div', {'class': re.compile("photo-gallery|PhotoGallery")}),
                                 ('div', {'id': "radePasteHelper"})],

    "COMPARE_NEW_IMAGE_IGNORE": [('img', {'width': "0"}),
                                 ('img', {'height': "0"}),
                                 ('img', {'src': re.compile("payment_calculator|demandforce_logo|fbcdn")}),
                                 ('div', {'class': re.compile("photo-gallery|PhotoGallery")}),
                                 ('img', {'data-photo': re.compile(".")})],

    # when checking images
    "CHECKING_IMAGE_IGNORE": [('img', {'src': re.compile("(registration|root)\.televox\.iapps\.com")})],

    # when checking homepage images
    "HOMEPAGE_IMAGE_IGNORE": [('div', {'id': re.compile("^(banner|primary-navigation)$")}),
                              ('img', {'runat': 'server'}),
                              ('img', {'src': re.compile("google|^data|fbcdn")})],

    # when checking homepage content
    "OLD_HOMEPAGE_CONTENT_IGNORE": [],

    "NEW_HOMEPAGE_CONTENT_IGNORE": [],

    # when checking homepage links
    "HOMEPAGE_LINK_IGNORE": [('div', {'id': re.compile('^(banner|primary-navigation)$')}),
                             ('li', {'class': "rmItem"}),
                             ('a', {'href': re.compile("javascript|fast\.wistia\.net")})],

    # when checking blog images
    "OLD_BLOG_IMAGE_IGNORE": [('header', {}),
                              ('img', {'width': "0"}),
                              ('img', {'height': "0"})],

    "NEW_BLOG_IMAGE_IGNORE": [('img', {'id': "featured_image"}),
                              ('img', {'src': re.compile("^fbcdn")})],

    # when checking blog links
    "OLD_BLOG_LINK_IGNORE": [('header', {}),
                             ('a', {'href': re.compile("jpg|png|pdf|mp4|UserFile|contentselector|#|javascript|fast\.wistia\.net")})],

    "NEW_BLOG_LINK_IGNORE": [('a', {'href': re.compile("jpg|png|pdf|mp4|UserFile|contentselector|#|javascript|fast\.wistia\.net")})],

    # when checking blog content
    "OLD_BLOG_CONTENT_IGNORE": [('header', {})],

    "NEW_BLOG_CONTENT_IGNORE": [('header', {})],

    # when checking form entries
    "OLD_FORM_ENTRY_IGNORE": [('p', {'class': "required-notice"}),
                              ('', {'string': re.compile("\bcode\b|\bCode\b")}),
                              ('div', {'class': "captcha"}),
                              ('div', {'id': re.compile("captcha")})],

    "NEW_FORM_ENTRY_IGNORE": [('p', {'class': "required-notice"}),
                              ('div', {'align': "right"}),
                              ('div', {'id': re.compile("captcha")}),
                              ('span', {'id': re.compile("FormTemplateName|CaptchaTitle")})],

    # dictionary for special character replacement
    "SPECIAL_CHARACTERS": [(u'\u2013', chr(45)),
                           (u'\u00a0', chr(32)),
                           (u'\u2019', chr(39)),
                           (u'\u201c', chr(34)),
                           (u'\u201d', chr(34)),
                           ('\t', ''),
                           (chr(59), '')],

}
