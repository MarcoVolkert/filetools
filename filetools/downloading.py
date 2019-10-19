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
    elements = tree.xpath(xpath)
    hrefs = [x.get("href") if x.get("href") else x.get("src") for x in elements]
    hrefs = [href for href in hrefs if href and contains in href]
    return hrefs


def downloadFiles(mainpage: str, name: str, sub_side="", g_xpath='//a', g_contains='', f_xpath='//a', f_contains="",
                  g_part=None, f_part=-1, ext="", cookies=None, paginator="", take_gallery_title=False):
    maindest = os.getcwd()
    mainname = _strip_url(mainpage)
    namedest = os.path.join(maindest, mainname, name.replace('/', '-'))
    os.makedirs(namedest, exist_ok=True)

    ofile = open(os.path.join(maindest, "download.txt"), 'a')
    http_path = _build_http_path(name, sub_side)
    galleries = getHrefs(mainpage + http_path, g_xpath, g_contains)
    if paginator:
        pagination_hrefs = getHrefs(mainpage + http_path, paginator)
        for paginationHref in pagination_hrefs:
            pagination_url = createUrl(paginationHref, mainpage)
            galleries += getHrefs(pagination_url, g_xpath, g_contains)

    for i, gallery in enumerate(galleries):
        if g_part:
            gallery_name = gallery.split("/")[g_part]
        else:
            gallery_name = '%03d' % i
        dest = os.path.join(namedest, gallery_name)
        print(dest)
        os.makedirs(dest, exist_ok=True)
        gallery_url = createUrl(gallery, mainpage)
        downloadFile(gallery_url, dest, cookies=cookies)
        file_urls = getHrefs(gallery_url, f_xpath, f_contains)
        if len(file_urls) == 0:
            print("no file urls found")
            continue
        ofile.write(" ".join([mainname, name, gallery_name, file_urls[0].split("/")[f_part], gallery]) + "\n")
        for j, file_url in enumerate(file_urls):
            file_url = createUrl(file_url, mainpage)
            filename = build_file_name(dest, file_urls, j, f_part, ext, gallery_url, take_gallery_title)
            download_file_direct(file_url, filename, headers={'Referer': gallery_url}, cookies=cookies)
    ofile.close()


def downloadFilesMulti(mainpage: str, names: List[str], sub_side="", g_xpath='//a', g_contains='', f_xpath='//a',
                       f_contains="", g_part=None, f_part=-1, ext="", cookies=None, paginator="",
                       take_gallery_title=False):
    for name in names:
        downloadFiles(mainpage=mainpage, name=name, sub_side=sub_side, g_xpath=g_xpath, g_contains=g_contains,
                      f_xpath=f_xpath, f_contains=f_contains,
                      g_part=g_part, f_part=f_part, ext=ext, cookies=cookies,
                      paginator=paginator, take_gallery_title=take_gallery_title)


def downloadFilesFromGallery(mainpage: str, subpage: str, xpath='', contains="", cookies=None):
    maindest = os.getcwd()
    mainname = _strip_url(mainpage)
    dest = os.path.join(maindest, mainname)
    os.makedirs(dest, exist_ok=True)

    gallery_url = mainpage + subpage
    file_urls = getHrefs(gallery_url, xpath, contains)
    os.makedirs(dest, exist_ok=True)
    for file_url in file_urls:
        file_url = createUrl(file_url, mainpage)
        downloadFile(file_url, dest, headers={'Referer': gallery_url}, cookies=cookies)


def firstAndLazyLoaded(mainpage: str, dirname: str, xpath='', contains="", cookies=None):
    maindest = os.getcwd()
    dest = os.path.join(maindest, dirname)
    os.makedirs(dest, exist_ok=True)

    file_urls = getHrefs(mainpage, xpath, contains)
    file_url = file_urls[0]
    for i in range(0, 100):
        contains_sub = contains.replace('0', i.__str__())
        file_url_new = file_url.replace(contains, contains_sub)
        try:
            downloadFile(file_url_new, dest, headers={'Referer': mainpage}, cookies=cookies)
        except Exception:
            break


def createUrl(url: str, mainpage: str) -> str:
    if not url.startswith('http'):
        return mainpage + url
    return url


def build_file_name(dest, file_urls: List[str], i: int, part=-1, ext="", gallery_url="", take_gallery_title=False):
    if take_gallery_title:
        gallery_title = os.path.join(dest, _url_to_filename(gallery_url, part))
        if len(file_urls) > 1:
            return gallery_title + '_%03d' % i + ext
        else:
            return gallery_title + ext
    else:
        return os.path.join(dest, _url_to_filename(file_urls[i], part, ext))


def downloadFile(url: str, dest="", part=-1, ext="", headers=None, cookies=None, do_throw=False, filename=""):
    if not filename:
        filename = os.path.join(dest, _url_to_filename(url, part, ext))
    return download_file_direct(url, filename, headers, cookies, do_throw)


def download_file_direct(url: str, filename: str, headers=None, cookies=None, do_throw=False):
    page_content = get_page_content(url, headers, cookies, do_throw)
    with open(filename, 'wb') as f:
        f.write(page_content)


def get_page_content(url: str, headers=None, cookies=None, do_throw=False) -> Optional[bytes]:
    if headers is None:
        headers = {}
    if cookies is None:
        cookies = {}
    print("get: " + url)
    page = requests.get(url, cookies=cookies, headers=headers)
    if page.status_code != 200:
        print("error in get " + url + " : " + page.status_code + "" + page.reason)
        if do_throw:
            raise Exception
    return page.content


def _strip_url(url: str) -> str:
    replacements = ['http://', 'https://', 'www.', '.com', '.de']
    name = url
    for replacement in replacements:
        name = name.replace(replacement, '')
    return name


def _build_http_path(name: str, sub_side="") -> str:
    http_path = '/'
    if sub_side:
        http_path += sub_side + '/'
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
