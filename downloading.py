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


def getHrefs(mainpage, subpage, css='', contains=''):
    print(mainpage + subpage)
    page = requests.get(mainpage + subpage)
    tree = html.fromstring(page.content)
    aList = tree.xpath('//a' + css)
    hrefs = [x.get("href") for x in aList]
    hrefs = [href for href in hrefs if href and contains in href]
    hrefs = [href if mainpage in href else mainpage + href for href in hrefs]
    return hrefs


def downloadPics(mainpage, name, subSide="", g_css='', g_contains='', p_css='', p_contains="",
                 use_gallery_name=True):
    maindest = os.getcwd()
    replacements = ['http://', 'www.', '.com', '.de']
    mainname = mainpage
    for replacement in replacements:
        mainname = mainname.replace(replacement, '')
    namedest = os.path.join(maindest, mainname, name)
    os.makedirs(namedest, exist_ok=True)

    ofile = open(os.path.join(maindest, "download.txt"), 'a')
    http_path = '/' + subSide + '/' + name
    if not name.endswith("html"):
        http_path += "/"
    galleries = getHrefs(mainpage, http_path, g_css, g_contains)
    for i, gallery in enumerate(galleries):
        if use_gallery_name:
            gallery_name = gallery.split("/")[-1]
        else:
            gallery_name = '%03d' % i
        dest = os.path.join(namedest, gallery_name)
        print(dest)
        os.makedirs(dest, exist_ok=True)
        pics = getHrefs(gallery, "", p_css, p_contains)
        ofile.write(" ".join([mainname, name, gallery_name, pics[0].split("/")[-1], gallery]) + "\n")
        for pic in pics:
            if use_gallery_name:
                downloadPdf(pic, dest)
            else:
                downloadFile(pic, dest)
    ofile.close()


def downloadPicsMulti(mainpage, names, subSide="", g_css='', g_contains='', p_css='', p_contains=""):
    for name in names:
        downloadPics(mainpage, name, subSide, g_css, g_contains, p_css, p_contains)


def downloadPicsFromGallery(mainpage, subpage, css='', contains=""):
    maindest = os.getcwd()
    mainname = mainpage.replace('http://', '').replace('.com', '')
    dest = os.path.join(maindest, mainname)
    os.makedirs(dest, exist_ok=True)

    pics = getHrefs(mainpage, subpage, css, contains)
    print(dest)
    os.makedirs(dest, exist_ok=True)
    for pic in pics:
        downloadFile(pic, dest)


def downloadFile(picUrl, dest):
    page = requests.get(picUrl)
    filename = os.path.join(dest, picUrl.split('/')[-1])
    with open(filename, 'wb') as f:
        f.write(page.content)


def downloadPdf(picUrl, dest):
    cookies = {"JSESSIONID": "3E7441071E5F19B7BC352A2A951F06B2.springboard3",
               "spr_prophy_cookie": "true",
               "springboard_user": "NG8zbzR2NDIxY3ZkanIxaG0x"}
    print(picUrl)
    page = requests.get(picUrl, cookies=cookies)
    filename = os.path.join(dest, picUrl.split('/')[-2] + ".pdf")
    with open(filename, 'wb') as f:
        f.write(page.content)
