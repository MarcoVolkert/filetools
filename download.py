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
    return hrefs


def downloadPics(mainpage, name, subSide="model", g_css='', g_contains='gallery', p_css='[@class="fancybox"]',
                 p_contains=""):
    maindest = os.getcwd()
    mainname = mainpage.replace('http://', '').replace('.com', '')
    namedest = maindest + mainname + '\\' + name
    os.makedirs(namedest, exist_ok=True)

    ofile = open(maindest + "download.txt", 'a')
    galleries = getHrefs(mainpage, '/' + subSide + '/' + name + '/', g_css, g_contains)
    for i, gallery in enumerate(galleries):
        dest = namedest + '\\%03d' % i
        print(dest)
        os.makedirs(dest, exist_ok=True)
        pics = getHrefs(mainpage, gallery, p_css, p_contains)
        ofile.write(name + " " + pics[0].split("/")[-1] + "\n")
        for pic in pics:
            downloadFile(pic, dest)
    ofile.close()


def downloadPicsFromGallery(mainpage, subpage, css='[@class="fancybox"]', contains=""):
    maindest = os.getcwd()
    mainname = mainpage.replace('http://', '').replace('.com', '')
    dest = maindest + mainname
    os.makedirs(dest, exist_ok=True)

    pics = getHrefs(mainpage, subpage, css, contains)
    print(dest)
    os.makedirs(dest, exist_ok=True)
    for pic in pics:
        downloadFile(pic, dest)


def downloadFile(picUrl, dest):
    page = requests.get(picUrl)
    filename = dest + '\\' + picUrl.split('/')[-1]
    with open(filename, 'wb') as f:
        f.write(page.content)


def downloadMulti():
    # names=['katy-rios','kiara-lord','sara-kay','vinna-reed','alice-march']
    # mainpage='http://alsscangirlz.com'
    # for name in names:
    #   downloadPics(mainpage,name)
    # names=['milla','jessica','foxy-di','silvie','angelica']
    # mainpage='http://matrixteens.com'
    # for name in names:
    #   downloadPics(mainpage,name)
    # names=['luba','selma','larisa-a','irishka','nikola','vera']
    # mainpage='http://xmodelpics.com'
    # for name in names:
    #   downloadPics(mainpage,name)
    names = ['nikia-a', "adel-c", "nastya-k"]
    mainpage = 'http://metartgirlz.com'
    for name in names:
        downloadPics(mainpage, name)
    # names = ['nikia-a']
    # mainpage = 'http://www.ametart.com'
    # for name in names:
    #   downloadPics(mainpage, name, pcontains="photos", pcss="",subSide="models")
    # names = ['jeff-milton', 'emily-bloom', 'kay-j', 'lena-anderson', 'zlatka-a', 'sigrid', 'augusta-crystal', 'daniel-sea']
    # mainpage = 'http://metartgirlz.com'
    # for name in names:
    #    downloadPics(mainpage, name)
    # names = ['lara','kisa','emily','mari','nensi','sunna','tina','rima','nelly']
    # names+= ['sofa', 'mila', 'bonita', 'lapa', 'tutty', 'chloe', 'brie', 'nikita', 'barbie','parisa']
    # mainpage = 'http://amourgirlz.com'
    # for name in names:
    #    downloadPics(mainpage, name)
