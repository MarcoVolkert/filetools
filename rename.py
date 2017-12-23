#!/usr/bin/env python3

"""
collection of rename operations
"""

__author__ = "Marco Volkert"
__copyright__ = "Copyright 2017, Marco Volkert"
__email__ = "marco.volkert24@gmx.de"
__status__ = "Development"

import os
# for reloading
from IPython import get_ipython

get_ipython().magic('reload_ext autoreload')

print('loaded collection of rename operations')


def setCounters(name="Name", start=1):
    inpath = setCounters.path + name
    dirCounter = start
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        if inpath == dirpath: continue
        fileCounter = 1
        for filename in filenames:
            newFilename = name + "_%02d_%02d" % (dirCounter, fileCounter) + ".jpg"
            os.rename(dirpath + "\\" + filename, inpath + "\\" + newFilename)
            fileCounter += 1
        dirCounter += 1


setCounters.path = "F:\\Video\\z_Bearbeitung\\new\\photoseries\\"


def setCountersMulti():
    inpath = setCounters.path
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        if not inpath == dirpath: continue
        for dirname in dirnames:
            setCounters(dirname)


def normalizeCountersKeepName(subpath="", write=False):
    import re
    if not subpath == "": subpath = "\\" + subpath
    inpath = normalizeCountersKeepName.path + subpath
    print(inpath)
    dirCounter = 1
    fileCounter = 1
    lastNameMain = ""
    lastNameMid = ""
    matchreg = r"^([-\w]+)_([0-9]+)_([0-9]+)"
    if write: _renameTemp(inpath)
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        for filename in filenames:
            match = re.search(matchreg, filename)
            if not match:
                print("no match", dirpath, filename)
                if write: _renameTempBack(dirpath, filename)
                continue
            nameMain = match.group(1)
            nameMid = match.group(2)
            if not nameMain == lastNameMain:
                dirCounter = 1
                fileCounter = 1
            elif not nameMid == lastNameMid:
                dirCounter += 1
                fileCounter = 1
            else:
                fileCounter += 1
            newFilename = nameMain + "_%02d_%02d" % (dirCounter, fileCounter) + ".jpg"
            print(newFilename)
            if write: _renameInPlace(dirpath, filename, newFilename)
            lastNameMain = nameMain
            lastNameMid = nameMid


normalizeCountersKeepName.path = "F:\\Video\\z_Bearbeitung\\Bilder\\sorted\\best"


def normalizeCountersMultiDirname(subpath=""):
    if not subpath == "": subpath = "\\" + subpath
    inpath = normalizeCounters.path + subpath
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        if not inpath == dirpath: continue
        for dirname in dirnames:
            print("renameIndexNorm2Multi:", dirname)
            normalizeCounters(dirname, dirname, 1)


def normalizeCountersMulti(subpath="", name=""):
    if not subpath == "": subpath = "\\" + subpath
    inpath = normalizeCounters.path + subpath
    dirCounter = 0
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        if not inpath == dirpath: continue
        for dirname in dirnames:
            dirCounter = normalizeCounters(dirname, name, dirCounter + 1)


def normalizeCounters(subpath="", name="", start=1, write=False):
    import re
    if not subpath == "": subpath = "\\" + subpath
    inpath = normalizeCounters.path + subpath
    if not name == "":  name += "_"
    dirCounter = start - 1
    fileCounter = 1
    lastNameMid = ""
    matchreg = r"([0-9]+)_([0-9]+)."
    if write: _renameTemp(inpath)
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        print("renameIndexNorm2:", dirpath)
        for filename in filenames:
            match = re.search(matchreg, filename)
            if not match:
                print("no match", dirpath, filename)
                if write: _renameTempBack(dirpath, filename)
                continue
            nameMid = match.group(1)
            if not nameMid == lastNameMid:
                dirCounter += 1
                fileCounter = 1
            else:
                fileCounter += 1
            newFilename = name + "%02d_%02d" % (dirCounter, fileCounter) + ".jpg"
            print(dirpath, newFilename)
            if write: _renameInPlace(dirpath, filename, newFilename)
            lastNameMid = nameMid
    return dirCounter


normalizeCounters.path = "F:\\Video\\z_Bearbeitung\\Bilder\\websites"


def normalizeCountersButKeepName(subpath="", name="", start=1, write=False):
    import re
    if not subpath == "": subpath = "\\" + subpath
    inpath = normalizeCountersKeepName.path + subpath
    print(inpath)
    dirCounter = start - 1
    fileCounter = 1
    lastNameMain = name
    lastNameMid = ""
    matchreg = r"^([-\w]+)_([0-9]+)_([0-9]+)"
    matchreg2 = r"([0-9]+)_([0-9]+)."
    if write: _renameTemp(inpath)
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        for filename in filenames:
            match = re.search(matchreg, filename)
            match2 = re.search(matchreg2, filename)
            if not match and not match2:
                print("no match", dirpath, filename)
                if write: _renameTempBack(dirpath, filename)
                continue
            if match:
                nameMain = name
                nameMid = match.group(1)
            elif match2:
                nameMain = match.group(1)
                nameMid = match.group(2)
            if not nameMain == lastNameMain:
                dirCounter = 1
                fileCounter = 1
            elif not nameMid == lastNameMid:
                dirCounter += 1
                fileCounter = 1
            else:
                fileCounter += 1
            newFilename = nameMain + "_%02d_%02d" % (dirCounter, fileCounter) + ".jpg"
            print(newFilename)
            if write: _renameInPlace(dirpath, filename, newFilename)
            lastNameMain = nameMain
            lastNameMid = nameMid


def FoldersToUpper(subpath="", write=True):
    # from name-sirname to Name Sirname
    if not subpath == "": subpath = "\\" + subpath
    inpath = FoldersToUpper.path + subpath
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        if not inpath == dirpath: continue
        for dirname in dirnames:
            parts = dirname.split('-')
            newName = ''
            for part in parts:
                newName += part[0].upper()
                newName += part[1:]
                newName += ' '
            newName = newName[:-1]
            print(newName)
            if write: _renameInPlace(dirpath, dirname, newName)


FoldersToUpper.path = "F:\\Video\\z_Bearbeitung\\new\\photoseries"


def _renameInPlace(dirpath, oldFilename, newFilename):
    os.rename(dirpath + "\\" + oldFilename, dirpath + "\\" + newFilename)


def _renameTemp(inpath):
    temppostfix = "temp"
    if not os.path.isdir(inpath):
        print('not found directory: ' + inpath)
        return
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        for filename in filenames:
            os.rename(dirpath + "\\" + filename, dirpath + "\\" + filename + temppostfix)
    return temppostfix


def _renameTempBack(dirpath, filename):
    newFilename = filename[:filename.rfind(".")] + ".jpg"
    _renameInPlace(dirpath, filename, newFilename)