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
from datetime import datetime
from http.cookies import SimpleCookie
from time import sleep
from typing import List, Union, Tuple
from enum import Enum
from filetools.helpers import makedirs
from lxml import html
import requests
from requests import Response

__all__ = ["downloadFiles", "downloadFilesFromGallery", "downloadFilesMulti", "firstAndLazyLoaded", "NameSource"]


class NameSource(Enum):
    URL = 0
    CONTENT = 1
    NAME = 2
    GALLERY = 3


def getHrefs(page, xpath='//a', contains='', cookies: dict = None, headers: dict = None) -> List[str]:
    response = get_response(page, cookies=cookies, headers=headers)
    if response.status_code != 200:
        return []
    tree = html.fromstring(response.content)
    elements = tree.xpath(xpath)
    hrefs = [x.get("href") if x.get("href") else x.get("src") for x in elements]
    hrefs = [href for href in hrefs if href and contains in href]
    return hrefs


def getContent(response: Response, xpath: str) -> List[str]:
    if response.status_code != 200 or not xpath:
        return []
    tree = html.fromstring(response.content)
    elements = tree.xpath(xpath)
    return [element.text_content() for element in elements]


def downloadFiles(mainpage: str, name: str, sub_side="", g_xpath='//a', g_contains='', f_xpath='//a', f_contains="",
                  g_part=-1, f_part=-1, ext="", cookies: Union[dict, str] = None, paginator="",
                  name_source: NameSource = NameSource.URL, start_after="", pretty_print=False, description_xpath='',
                  statistic_only=False):
    if isinstance(cookies, str):
        cookies = _cookie_string_2_dict(cookies)

    # determine url of overview pages
    http_path = _build_http_path(mainpage, sub_side, name)
    urls = [http_path]
    if paginator:
        pagination_hrefs = getHrefs(http_path, paginator, cookies=cookies)
        for paginationHref in pagination_hrefs:
            pagination_url = _createUrl(paginationHref, mainpage)
            urls.append(pagination_url)

    # extract galleries
    galleries = []
    for url in urls:
        galleries += getHrefs(url, g_xpath, g_contains, cookies=cookies)
    if not galleries:
        return

    galleries.reverse()
    dest_main = os.getcwd()
    dirname_mainpage = _strip_url(mainpage)
    dirname_name = name.replace('/', '-')
    if pretty_print:
        dirname_name = pretty_name(dirname_name)
    dest_name = makedirs(dest_main, dirname_mainpage, dirname_name)
    dest_html = makedirs(dest_main, dirname_mainpage, 'html', dirname_name)
    html_list = download_html(urls, dest_html, dirname_name, cookies)
    html_title = getContent(html_list[0][0], r"//title")[0]
    html_description = getContent(html_list[0][0], description_xpath)
    _log_name(dest_main, dirname_mainpage, dirname_name, galleries, html_title, html_description, http_path)
    found = False

    for i, gallery in enumerate(galleries):
        gallery_title = _strip_url(_extract_part(gallery, g_part))
        if start_after and not found:
            found = start_after == gallery_title
            continue
        dirname_gallery = '%03d_%s' % (i + 1, gallery_title)
        gallery_url = _createUrl(gallery, mainpage)
        file_urls = getHrefs(gallery_url, f_xpath, f_contains, cookies=cookies)

        if len(file_urls) == 0:
            print("no file urls found")
            continue
        elif len(file_urls) == 1:
            dest_gallery = dest_name
        else:
            dest_gallery = os.path.join(dest_name, dirname_gallery)
            if os.path.exists(dest_gallery):
                continue
            os.makedirs(dest_gallery)
        print(dest_gallery)
        download_html([gallery_url], dest_html, dirname_gallery, cookies)

        for j, file_url in enumerate(file_urls):
            file_url = _createUrl(file_url, mainpage)
            filename = _build_file_name(file_urls, j, f_part, ext, dirname_name, i, gallery_title, name_source)
            if j == 0:
                _log_gallery(dest_main, dirname_mainpage, dirname_name, dirname_gallery, filename, file_urls, gallery)
            if not statistic_only:
                download_file_direct(file_url, dest_gallery, filename, cookies=cookies, headers={'Referer': gallery_url})


def downloadFilesMulti(mainpage: str, names: List[str], sub_side="", g_xpath='//a', g_contains='', f_xpath='//a',
                       f_contains="", g_part=-1, f_part=-1, ext="", cookies: Union[dict, str] = None, paginator="",
                       name_source: NameSource = NameSource.URL, pretty_print=False, description_xpath='',
                       statistic_only=False):
    for name in names:
        downloadFiles(mainpage=mainpage, name=name, sub_side=sub_side, g_xpath=g_xpath, g_contains=g_contains,
                      f_xpath=f_xpath, f_contains=f_contains,
                      g_part=g_part, f_part=f_part, ext=ext, cookies=cookies,
                      paginator=paginator, name_source=name_source, pretty_print=pretty_print,
                      description_xpath=description_xpath, statistic_only=statistic_only)


def downloadFilesFromGallery(mainpage: str, subpage: str, xpath='//a', contains="", part=-1, ext="",
                             cookies: Union[dict, str] = None):
    if isinstance(cookies, str):
        cookies = _cookie_string_2_dict(cookies)
    maindest = os.getcwd()
    mainname = _strip_url(mainpage)
    subpage_dirname = subpage.replace('/', '-')
    dest = os.path.join(maindest, mainname, subpage_dirname)
    os.makedirs(dest, exist_ok=True)

    gallery_url = _build_http_path(mainpage, subpage)
    file_urls = getHrefs(gallery_url, xpath, contains, cookies=cookies)
    downloadFile(gallery_url, dest, filename="%s.html" % subpage_dirname, cookies=cookies)
    for file_url in file_urls:
        file_url = _createUrl(file_url, mainpage)
        downloadFile(file_url, dest, part=part, ext=ext, cookies=cookies, headers={'Referer': gallery_url})


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
                 do_throw=False) -> Tuple[Response, str]:
    print(filename)
    if not filename:
        filename = _url_to_filename(url, part, ext)
    return download_file_direct(url, dest, filename, cookies, headers, do_throw)


def download_file_direct(url: str, dest: str, filename: str, cookies: dict = None, headers: dict = None,
                         do_throw=False, name_source: NameSource = NameSource.URL) -> Tuple[Response, str]:
    url = _strip_options(url)
    response = get_response(url, cookies, headers, do_throw)
    if response.status_code != 200:
        return response, ""
    if name_source == NameSource.CONTENT:
        response_filename = _extract_filename_from_response(response)
        if response_filename:
            filename = response_filename
    filepath = os.path.join(dest, filename)
    with open(filepath, 'wb') as f:
        f.write(response.content)
    return response, filepath


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


def download_html(urls: List[str], dest: str, filename: str, cookies: dict = None) -> List[Tuple[Response, str]]:
    if len(urls) == 1:
        return [downloadFile(urls[0], dest, filename="%s.html" % filename, cookies=cookies)]
    else:
        return [downloadFile(url, dest, filename="%s_p%02d.html" % (filename, i + 1), cookies=cookies)
                for i, url in enumerate(urls)]


def _strip_url(url: str) -> str:
    replacements = ['http://', 'https://', 'www.', '.com', '.de', '.html']
    name = _strip_options(url)
    for replacement in replacements:
        name = name.replace(replacement, '')
    return name


def _build_http_path(mainpage: str, sub_side: str, name: str = "") -> str:
    http_path = ''
    if sub_side:
        http_path += '/' + sub_side
    if name:
        http_path += '/' + name
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


def _build_file_name(file_urls: List[str], file_counter: int, part=-1, ext="", name: str = "", gallery_counter: int = 0,
                     gallery_title: str = "", name_source: NameSource = NameSource.URL) -> str:
    if name_source == NameSource.URL or name_source == NameSource.CONTENT:
        return _url_to_filename(file_urls[file_counter], part, ext)
    filename = ""
    if name_source == NameSource.GALLERY:
        filename = '%03d_%s' % (gallery_counter + 1, gallery_title)
    elif name_source == NameSource.NAME:
        filename = '%s_%03d' % (name, gallery_counter + 1)
    if len(file_urls) > 1:
        return filename + '_%03d' % (file_counter + 1) + ext
    else:
        return filename + ext


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


def _log_name(dest_main: str, dirname_mainpage: str, dirname_name: str, galleries: List[str], html_title: str,
              html_description: List[str], http_path: str):
    ofilename = os.path.join(dest_main, "download1_names.csv")
    ofile_exists = os.path.isfile(ofilename)
    with open(ofilename, 'a') as ofile:
        if not ofile_exists:
            ofile.write(";".join(
                ["dirname_mainpage", "dirname_name", "number-of-galleries", "download-source-name", "download-title",
                 "download-description", "download-date"]) + "\n")
        ofile.write(";".join(
            [dirname_mainpage, dirname_name, str(len(galleries)), http_path, html_title, ",".join(html_description),
             str(datetime.now())]) + "\n")


def _log_gallery(dest_main: str, dirname_mainpage: str, dirname_name: str, dirname_gallery: str, filename: str,
                 file_urls: List[str], gallery: str):
    ofilename = os.path.join(dest_main, "download2_galleries.csv")
    ofile_exists = os.path.isfile(ofilename)
    with open(ofilename, 'a') as ofile:
        if not ofile_exists:
            ofile.write(";".join(
                ["dirname_mainpage", "dirname_name", "dirname_gallery", "filename", "number-of-files",
                 "download-source-gallery", "download-date"]) + "\n")
        ofile.write(";".join(
            [dirname_mainpage, dirname_name, dirname_gallery, filename, str(len(file_urls)), gallery,
             str(datetime.now())]) + "\n")


def pretty_name(name: str) -> str:
    parts = name.split('-')
    new_name = ''
    for part in parts:
        new_name += part[0].upper()
        new_name += part[1:]
        new_name += ' '
    return new_name[:-1]
