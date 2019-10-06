#!/usr/bin/env python3

"""
collection of download operations
http://docs.python-guide.org/en/latest/scenarios/scrape/
http://stackabuse.com/download-files-with-python/
"""
from typing import List, Optional

__author__ = "Marco Volkert"
__copyright__ = "Copyright 2017, Marco Volkert"
__email__ = "marco.volkert24@gmx.de"
__status__ = "Development"

from lxml import html
import requests
import os

__all__ = ["downloadFiles", "downloadFilesFromGallery", "downloadFilesMulti", "firstAndLazyLoaded"]


def getHrefs(page, xpath='//a', contains='', headers=None, cookies=None) -> List[str]:
    tree = html.fromstring(get_page_content(page, headers=headers, cookies=cookies))
    aList = tree.xpath(xpath)
    hrefs = [x.get("href") if x.get("href") else x.get("src") for x in aList]
    hrefs = [href for href in hrefs if href and contains in href]
    return hrefs


def downloadFiles(mainpage: str, name: str, subSide="", g_xpath='//a', g_contains='', f_xpath='//a', f_contains="",
                  g_part=None, f_part=-1, ext="", cookies=None, paginator=""):
    maindest = os.getcwd()
    mainname = _strip_url(mainpage)
    namedest = os.path.join(maindest, mainname, name.replace('/', '-'))
    os.makedirs(namedest, exist_ok=True)

    ofile = open(os.path.join(maindest, "download.txt"), 'a')
    http_path = _build_http_path(name, subSide)
    galleries = getHrefs(mainpage + http_path, g_xpath, g_contains)
    if paginator:
        paginationHrefs = getHrefs(mainpage + http_path, paginator)
        for paginationHref in paginationHrefs:
            paginationUrl = createUrl(paginationHref, mainpage)
            galleries += getHrefs(paginationUrl, g_xpath, g_contains)

    for i, gallery in enumerate(galleries):
        if g_part:
            gallery_name = gallery.split("/")[g_part]
        else:
            gallery_name = '%03d' % i
        dest = os.path.join(namedest, gallery_name)
        print(dest)
        os.makedirs(dest, exist_ok=True)
        galleryUrl = createUrl(gallery, mainpage)
        downloadFile(galleryUrl, dest, cookies=cookies)
        fileUrls = getHrefs(galleryUrl, f_xpath, f_contains)
        ofile.write(" ".join([mainname, name, gallery_name, fileUrls[0].split("/")[f_part], gallery]) + "\n")
        for fileUrl in fileUrls:
            fileUrl = createUrl(fileUrl, mainpage)
            downloadFile(fileUrl, dest, f_part, ext, headers={'Referer': galleryUrl}, cookies=cookies)
    ofile.close()


def downloadFilesMulti(mainpage: str, names: str, subSide="", g_xpath='//a', g_contains='', f_xpath='//a',
                       f_contains="", g_part=None, f_part=-1, ext="", cookies=None, paginator=""):
    for name in names:
        downloadFiles(mainpage=mainpage, name=name, subSide=subSide, g_xpath=g_xpath, g_contains=g_contains,
                      f_xpath=f_xpath, f_contains=f_contains,
                      g_part=g_part, f_part=f_part, ext=ext, cookies=cookies,
                      paginator=paginator)


def downloadFilesFromGallery(mainpage: str, subpage: str, xpath='', contains="", cookies=None):
    maindest = os.getcwd()
    mainname = _strip_url(mainpage)
    dest = os.path.join(maindest, mainname)
    os.makedirs(dest, exist_ok=True)

    galleryUrl = mainpage + subpage
    fileUrls = getHrefs(galleryUrl, xpath, contains)
    os.makedirs(dest, exist_ok=True)
    for fileUrl in fileUrls:
        fileUrl = createUrl(fileUrl, mainpage)
        downloadFile(fileUrl, dest, headers={'Referer': galleryUrl}, cookies=cookies)


def firstAndLazyLoaded(mainpage: str, dirname: str, xpath='', contains="", cookies=None):
    maindest = os.getcwd()
    dest = os.path.join(maindest, dirname)
    os.makedirs(dest, exist_ok=True)

    fileUrls = getHrefs(mainpage, xpath, contains)
    fileUrl = fileUrls[0]
    for i in range(0, 100):
        contains_sub = contains.replace('0', i.__str__())
        fileUrl_new = fileUrl.replace(contains, contains_sub)
        try:
            downloadFile(fileUrl_new, dest, headers={'Referer': mainpage}, cookies=cookies)
        except Exception:
            break


def createUrl(url: str, mainpage: str) -> str:
    if not url.startswith('http'):
        return mainpage + url
    return url


def downloadFile(url: str, dest: str, part=-1, ext="", headers=None, cookies=None, doThrow=False):
    page_content = get_page_content(url, headers, cookies, doThrow)
    filename = os.path.join(dest, _url_to_filename(url, part, ext))
    with open(filename, 'wb') as f:
        f.write(page_content)


def get_page_content(url: str, headers=None, cookies=None, doThrow=False) -> Optional[bytes]:
    if headers is None:
        headers = {}
    if cookies is None:
        cookies = {}
    print("get: " + url)
    page = requests.get(url, cookies=cookies, headers=headers)
    if page.status_code != 200:
        print("error in get " + url + " : " + page.status_code + "" + page.reason)
        if doThrow:
            raise Exception
    return page.content


def _strip_url(url: str) -> str:
    replacements = ['http://', 'https://', 'www.', '.com', '.de']
    name = url
    for replacement in replacements:
        name = name.replace(replacement, '')
    return name


def _build_http_path(name: str, subSide="") -> str:
    http_path = '/'
    if subSide:
        http_path += subSide + '/'
    http_path += name
    if not name.endswith("html"):
        http_path += "/"
    return http_path


def _url_to_filename(url: str, part=-1, ext="") -> str:
    filename = url.split('/')[part]
    filename = filename[:filename.rfind("?")]
    if ext:
        filename = filename.rsplit(".", 1)[0] + ext
    if not filename:
        filename = "index.html"
    return filename
