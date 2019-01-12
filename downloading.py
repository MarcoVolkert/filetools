#!/usr/bin/env python3

"""
collection of download operations
http://docs.python-guide.org/en/latest/scenarios/scrape/
http://stackabuse.com/download-files-with-python/
"""

__author__ = "Marco Volkert"
__copyright__ = "Copyright 2017, Marco Volkert"
__email__ = "marco.volkert24@gmx.de"
__status__ = "Development"

from lxml import html
import requests
import os


def getHrefs(page, css='', contains=''):
    tree = html.fromstring(get_page_content(page))
    aList = tree.xpath('//a' + css)
    hrefs = [x.get("href") for x in aList]
    hrefs = [href for href in hrefs if href and contains in href]
    return hrefs


def downloadFiles(mainpage, name, subSide="", g_css='', g_contains='', f_css='', f_contains="",
                  g_part=None, f_part=-1, ext=""):
    maindest = os.getcwd()
    mainname = _strip_url(mainpage)
    namedest = os.path.join(maindest, mainname, name.replace('/', '-'))
    os.makedirs(namedest, exist_ok=True)

    ofile = open(os.path.join(maindest, "download.txt"), 'a')
    http_path = _build_http_path(name, subSide)
    galleries = getHrefs(mainpage + http_path, g_css, g_contains)
    for i, gallery in enumerate(galleries):
        if g_part:
            gallery_name = gallery.split("/")[g_part]
        else:
            gallery_name = '%03d' % i
        dest = os.path.join(namedest, gallery_name)
        print(dest)
        os.makedirs(dest, exist_ok=True)
        downloadFile(mainpage + gallery, dest)
        fileUrls = getHrefs(mainpage + gallery, f_css, f_contains)
        ofile.write(" ".join([mainname, name, gallery_name, fileUrls[0].split("/")[f_part], gallery]) + "\n")
        for fileUrl in fileUrls:
            if mainpage not in fileUrl:
                fileUrl = mainpage + fileUrl
            downloadFile(fileUrl, dest, f_part, ext)
    ofile.close()


def downloadFilesMulti(mainpage, names, subSide="", g_css='', g_contains='', f_css='', f_contains=""):
    for name in names:
        downloadFiles(mainpage, name, subSide, g_css, g_contains, f_css, f_contains)


def downloadFilesFromGallery(mainpage, subpage, css='', contains=""):
    maindest = os.getcwd()
    mainname = _strip_url(mainpage)
    dest = os.path.join(maindest, mainname)
    os.makedirs(dest, exist_ok=True)

    pics = getHrefs(mainpage + subpage, css, contains)
    os.makedirs(dest, exist_ok=True)
    for pic in pics:
        downloadFile(pic, dest)


def downloadFile(url, dest, part=-1, ext=""):
    filename = os.path.join(dest, _url_to_filename(url, part, ext))
    with open(filename, 'wb') as f:
        f.write(get_page_content(url))


def get_page_content(url):
    print("get: " + url)
    page = requests.get(url, cookies=get_page_content.cookies)
    return page.content


get_page_content.cookies = {"JSESSIONID": "3E7441071E5F19B7BC352A2A951F06B2.springboard3",
                            "spr_prophy_cookie": "true",
                            "springboard_user": "NG8zbzR2NDIxY3ZkanIxaG0x"}


def _strip_url(url):
    replacements = ['http://', 'www.', '.com', '.de']
    name = url
    for replacement in replacements:
        name = name.replace(replacement, '')
    return name


def _build_http_path(name, subSide="") -> str:
    http_path = '/'
    if subSide:
        http_path += subSide + '/'
    http_path += name
    if not name.endswith("html"):
        http_path += "/"
    return http_path


def _url_to_filename(url, part=-1, ext="") -> str:
    filename = url.split('/')[part]
    if ext:
        filename = filename.rsplit(".", 1)[0] + ext
    if not filename:
        filename = "index.html"
    return filename
