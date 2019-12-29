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

import os
import re
from http.cookies import SimpleCookie
from time import sleep
from typing import List, Union
from lxml import html
import requests
from requests import Response

__all__ = ["downloadFiles", "downloadFilesFromGallery", "downloadFilesMulti", "firstAndLazyLoaded"]


def getHrefs(page, xpath='//a', contains='', cookies: dict = None, headers: dict = None) -> List[str]:
    response = get_response(page, cookies=cookies, headers=headers)
    tree = html.fromstring(response.content)
    elements = tree.xpath(xpath)
    hrefs = [x.get("href") if x.get("href") else x.get("src") for x in elements]
    hrefs = [href for href in hrefs if href and contains in href]
    return hrefs


def downloadFiles(mainpage: str, name: str, sub_side="", g_xpath='//a', g_contains='', f_xpath='//a', f_contains="",
                  g_part=-1, f_part=-1, ext="", cookies: Union[dict, str] = None, paginator="",
                  take_gallery_title=False, start_after=""):
    if isinstance(cookies, str):
        cookies = _cookie_string_2_dict(cookies)
    maindest = os.getcwd()
    mainname = _strip_url(mainpage)
    name_dirname = name.replace('/', '-')
    dest_name = os.path.join(maindest, mainname, name_dirname)
    dest_html = os.path.join(dest_name, 'html')
    os.makedirs(dest_html, exist_ok=True)

    ofile = open(os.path.join(maindest, "download.txt"), 'a')
    http_path = _build_http_path(name, sub_side, mainpage)
    downloadFile(http_path, dest_html, filename="%s.html" % name_dirname, cookies=cookies)
    galleries = getHrefs(http_path, g_xpath, g_contains, cookies=cookies)
    if paginator:
        pagination_hrefs = getHrefs(http_path, paginator, cookies=cookies)
        for i, paginationHref in enumerate(pagination_hrefs):
            pagination_url = _createUrl(paginationHref, mainpage)
            downloadFile(pagination_url, dest_html, filename="%s_p%d.html" % (name_dirname, i + 2), cookies=cookies)
            galleries += getHrefs(pagination_url, g_xpath, g_contains, cookies=cookies)
    galleries.reverse()
    found = False

    for i, gallery in enumerate(galleries):
        gallery_title = _strip_url(_extract_part(gallery, g_part))
        if start_after and not found:
            found = start_after == gallery_title
            continue
        gallery_dirname = '%03d_%s' % (i, gallery_title)
        gallery_url = _createUrl(gallery, mainpage)
        downloadFile(gallery_url, dest_html, filename="%s.html" % gallery_dirname, cookies=cookies)
        file_urls = getHrefs(gallery_url, f_xpath, f_contains, cookies=cookies)

        if len(file_urls) == 0:
            print("no file urls found")
            continue
        elif len(file_urls) == 1:
            dest_gallery = dest_name
        else:
            dest_gallery = os.path.join(dest_name, gallery_dirname)
            if os.path.exists(dest_gallery):
                continue
            os.makedirs(dest_gallery)
        print(dest_gallery)

        for j, file_url in enumerate(file_urls):
            file_url = _createUrl(file_url, mainpage)
            filename = _build_file_name(file_urls, j, f_part, ext, gallery_title, take_gallery_title)
            if j == 0:
                ofile.write(" ".join([mainname, name, gallery_dirname, filename, gallery]) + "\n")
            download_file_direct(file_url, dest_gallery, filename, cookies=cookies, headers={'Referer': gallery_url})
    ofile.close()


def downloadFilesMulti(mainpage: str, names: List[str], sub_side="", g_xpath='//a', g_contains='', f_xpath='//a',
                       f_contains="", g_part=-1, f_part=-1, ext="", cookies: Union[dict, str] = None, paginator="",
                       take_gallery_title=False):
    for name in names:
        downloadFiles(mainpage=mainpage, name=name, sub_side=sub_side, g_xpath=g_xpath, g_contains=g_contains,
                      f_xpath=f_xpath, f_contains=f_contains,
                      g_part=g_part, f_part=f_part, ext=ext, cookies=cookies,
                      paginator=paginator, take_gallery_title=take_gallery_title)


def downloadFilesFromGallery(mainpage: str, subpage: str, xpath='', contains="", cookies: Union[dict, str] = None):
    if isinstance(cookies, str):
        cookies = _cookie_string_2_dict(cookies)
    maindest = os.getcwd()
    mainname = _strip_url(mainpage)
    subpage_dirname = subpage.replace('/', '-')
    dest = os.path.join(maindest, mainname, subpage_dirname)
    os.makedirs(dest, exist_ok=True)

    gallery_url = _createUrl(subpage, mainpage)
    file_urls = getHrefs(gallery_url, xpath, contains, cookies=cookies)
    for file_url in file_urls:
        file_url = _createUrl(file_url, mainpage)
        downloadFile(file_url, dest, cookies=cookies, headers={'Referer': gallery_url})


def firstAndLazyLoaded(mainpage: str, dirname: str, xpath='', contains="", cookies: dict = None):
    maindest = os.getcwd()
    dest = os.path.join(maindest, dirname)
    os.makedirs(dest, exist_ok=True)

    file_urls = getHrefs(mainpage, xpath, contains, cookies=cookies)
    file_url = file_urls[0]
    for i in range(0, 100):
        contains_sub = contains.replace('0', i.__str__())
        file_url_new = file_url.replace(contains, contains_sub)
        try:
            downloadFile(file_url_new, dest, cookies=cookies, headers={'Referer': mainpage})
        except Exception:
            break


def downloadFile(url: str, dest: str, filename="", part=-1, ext="", cookies: dict = None, headers: dict = None,
                 do_throw=False):
    print(filename)
    if not filename:
        filename = _url_to_filename(url, part, ext)
    return download_file_direct(url, dest, filename, cookies, headers, do_throw)


def download_file_direct(url: str, dest: str, filename: str, cookies: dict = None, headers: dict = None,
                         do_throw=False) -> str:
    url = _strip_options(url)
    response = get_response(url, cookies, headers, do_throw)
    response_filename = _extract_filename_from_response(response)
    if response_filename:
        filename = response_filename
    filepath = os.path.join(dest, filename)
    with open(filepath, 'wb') as f:
        f.write(response.content)
    return filepath


def get_response(url: str, cookies: dict = None, headers: dict = None, do_throw=False) -> Response:
    if cookies is None:
        cookies = {}
    if headers is None:
        headers = {}
    headers['Connection'] = 'keep-alive'
    print("get: " + url)
    try:
        response = requests.get(url, cookies=cookies, headers=headers)
    except (requests.exceptions.ConnectionError, OSError) as e:
        print("got exception maybe to many requests - try again", e)
        sleep(30)
        response = requests.get(url, cookies=cookies, headers=headers)
    if response.status_code != 200:
        print("error in get " + url + " : " + str(response.status_code) + "" + response.reason)
        if do_throw:
            raise Exception
    return response


def _strip_url(url: str) -> str:
    replacements = ['http://', 'https://', 'www.', '.com', '.de', '.html']
    name = _strip_options(url)
    for replacement in replacements:
        name = name.replace(replacement, '')
    return name


def _build_http_path(name: str, sub_side="", mainpage="") -> str:
    http_path = '/'
    if sub_side:
        http_path += sub_side + '/'
    http_path += name
    if not name.endswith("html"):
        http_path += "/"
    return _createUrl(http_path, mainpage)


def _createUrl(url: str, mainpage: str = "") -> str:
    if not url.startswith('http'):
        if mainpage and mainpage.startswith('http'):
            return mainpage + url
        else:
            print("warning: url does not start with http ", url)
    return url


def _build_file_name(file_urls: List[str], i: int, part=-1, ext="", gallery_title="", take_gallery_title=False) -> str:
    if take_gallery_title:
        if len(file_urls) > 1:
            return gallery_title + '_%03d' % i + ext
        else:
            return gallery_title + ext
    else:
        return _url_to_filename(file_urls[i], part, ext)


def _url_to_filename(url: str, part: int = -1, ext="") -> str:
    filename = _extract_part(url, part)
    if ext:
        filename = filename.rsplit(".", 1)[0] + ext
    if not filename:
        filename = "index.html"
    return filename


def _extract_part(url: str, part: int) -> str:
    url = _strip_options(url)
    return url.split('/')[part]


def _strip_options(url: str) -> str:
    if "?" in url:
        return url[:url.rfind("?")]
    return url


def _extract_filename_from_response(response: Response):
    filename_key = "Content-Disposition"
    if filename_key in response.headers:
        disposition = response.headers[filename_key]
        filename = re.findall(r"filename\*?=([^;]+)", disposition, flags=re.IGNORECASE)
        return filename[0].strip().strip('"')
    return None


def _cookie_string_2_dict(cookie_string: str) -> dict:
    cookie = SimpleCookie()
    cookie.load(cookie_string)

    # Even though SimpleCookie is dictionary-like, it internally uses a Morsel object
    # which is incompatible with requests. Manually construct a dictionary instead.
    cookies = {}
    for key, morsel in cookie.items():
        cookies[key] = morsel.value
    return cookies
