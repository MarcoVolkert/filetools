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
    page = requests.get(mainpage + subpage)
    tree = html.fromstring(page.content)
    aList = tree.xpath('//a' + css)
    hrefs = [x.get("href") for x in aList]
    hrefs = [x for x in hrefs if contains in x]
    # print(hrefs)
    return hrefs


def downloadPics(mainpage, name):
    maindest = 'F:\\Video\\z_Bearbeitung\\new\\photoseries\\'
    mainname = mainpage.replace('http://', '').replace('.com', '')
    namedest = maindest + mainname + '\\' + name
    os.makedirs(namedest, exist_ok=True)

    galleries = getHrefs(mainpage, '/model/' + name + '/', contains='gallery')
    for i, gallery in enumerate(galleries):
        pics = getHrefs(mainpage, gallery, css='[@class="fancybox"]')
        dest = namedest + '\\' + str(i)
        print(dest)
        os.makedirs(dest, exist_ok=True)
        for pic in pics:
            downloadFile(pic, dest)


def downloadPicsFromGallery():
    mainpage = "http://amourgirlz.com"
    maindest = 'F:\\Video\\z_Bearbeitung\\new\\photoseries\\'
    mainname = mainpage.replace('http://', '').replace('.com', '')
    namedest = maindest + mainname
    os.makedirs(namedest, exist_ok=True)
    gallery = "/gallery/teen-strips-outdoors/"

    pics = getHrefs(mainpage, gallery, css='[@class="fancybox"]')
    dest = namedest
    print(dest)
    os.makedirs(dest, exist_ok=True)
    for pic in pics:
        downloadFile(pic, dest)

def downloadFile(picUrl, dest):
    page = requests.get(picUrl)
    filename = dest + '\\' + picUrl.split('/')[-1]
    # print(filename)
    with open(filename, 'wb') as f:
        f.write(page.content)


def downloadMulti():
    names = ['daniel-sea']
    mainpage = 'http://www.ametart.com'
    for name in names:
        downloadPics(mainpage, name)
