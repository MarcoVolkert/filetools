#!/usr/bin/env python3

"""
collection of rename operations
"""

__author__ = "Marco Volkert"
__copyright__ = "Copyright 2017, Marco Volkert"
__email__ = "marco.volkert24@gmx.de"
__status__ = "Development"

import os
import re
# for reloading
from IPython import get_ipython

get_ipython().magic('reload_ext autoreload')

print('loaded collection of rename operations')


def setCounters(name="Name", start=1, subpath=""):
    inpath = _concatPath(setCounters.path, subpath) + "\\" + name
    dirCounter = start
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        if inpath == dirpath: continue
        print(dirpath)
        fileCounter = 1
        for filename in filenames:
            newFilename = _getNewName(name, dirCounter, fileCounter)
            os.rename(dirpath + "\\" + filename, inpath + "\\" + newFilename)
            fileCounter += 1
        dirCounter += 1
        _removeIfEmtpy(dirpath)


setCounters.path = "F:\\Video\\z_Bearbeitung\\new\\photoseries"


def setCountersMulti(subpath=""):
    inpath = _concatPath(setCounters.path, subpath)
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        if not inpath == dirpath: continue
        print(dirpath)
        for dirname in dirnames:
            setCounters(dirname, subpath=subpath)


def normalizeCountersKeepName(subpath="", write=False):
    inpath = _concatPath(normalizeCountersKeepName.path, subpath)
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
            newFilename = _getNewName(nameMain, dirCounter, fileCounter)
            print(newFilename)
            if write: _renameInPlace(dirpath, filename, newFilename)
            lastNameMain = nameMain
            lastNameMid = nameMid


normalizeCountersKeepName.path = "F:\\Video\\z_Bearbeitung\\Bilder\\sorted\\best"


def normalizeCountersMultiDirname(subpath=""):
    inpath = _concatPath(normalizeCounters.path, subpath)
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        if not inpath == dirpath: continue
        for dirname in dirnames:
            print("renameIndexNorm2Multi:", dirname)
            normalizeCounters(dirname, dirname, 1)


def normalizeCountersMulti(subpath="", name=""):
    inpath = _concatPath(normalizeCounters.path, subpath)
    dirCounter = 0
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        if not inpath == dirpath: continue
        for dirname in dirnames:
            dirCounter = normalizeCounters(dirname, name, dirCounter + 1)


def normalizeCounters(subpath="", name="", start=1, write=False):
    inpath = _concatPath(normalizeCounters.path, subpath)
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
            newFilename = _getNewName(name, dirCounter, fileCounter)
            print(dirpath, newFilename)
            if write: _renameInPlace(dirpath, filename, newFilename)
            lastNameMid = nameMid
    return dirCounter


normalizeCounters.path = "F:\\Video\\z_Bearbeitung\\Bilder\\websites"


def normalizeCountersButKeepName(subpath="", name="", start=1, write=False):
    inpath = _concatPath(normalizeCountersButKeepName.path, subpath)
    dirCounter = start - 1
    normalDirCounter = dirCounter
    fileCounter = 1
    lastNameMain = name
    lastNameMid = ""
    matchregName = r"^([-\w]+)_([0-9]+)_([0-9]+)"
    matchreg = r"([0-9]+)_([0-9]+)."
    if write: _renameTemp(inpath)
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        for filename in filenames:
            matchName = re.search(matchregName, filename)
            match = re.search(matchreg, filename)
            if matchName:
                nameMain = matchName.group(1)
                if not nameMain == lastNameMain:
                    dirCounter = 0
            elif match:
                nameMain = name
                if not nameMain == lastNameMain:
                    dirCounter = normalDirCounter
            else:
                print("no match", dirpath, filename)
                if write: _renameTempBack(dirpath, filename)
                continue
            nameMid = match.group(1)
            if not nameMid == lastNameMid:
                dirCounter += 1
                fileCounter = 1
            else:
                fileCounter += 1
            if not matchName and match: normalDirCounter = dirCounter
            newFilename = _getNewName(nameMain, dirCounter, fileCounter)
            print(newFilename)
            if write: _renameInPlace(dirpath, filename, newFilename)
            lastNameMain = nameMain
            lastNameMid = nameMid


normalizeCountersButKeepName.path = "F:\\Video\\z_Bearbeitung\\Bilder\\websites"


def FoldersToUpper(subpath="", write=True):
    # from name-sirname to Name Sirname
    inpath = _concatPath(FoldersToUpper.path, subpath)
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
    if not os.path.isdir(inpath):
        print('not found directory: ' + inpath)
        return
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        for filename in filenames:
            _renameInPlace(dirpath, filename, filename + _renameTemp.temppostfix)
    return _renameTemp.temppostfix


_renameTemp.temppostfix = "temp"


def _renameTempBack(dirpath, filename):
    newFilename = re.sub(_renameTemp.temppostfix + '$', '', filename)
    _renameInPlace(dirpath, filename, newFilename)


def _concatPath(path, subpath):
    if not subpath == "": subpath = "\\" + subpath
    fullpath = path + subpath
    print(fullpath)
    return fullpath


def _getNewName(name, dirCounter, fileCounter):
    if name: name += "_"
    return name + "%02d_%02d" % (dirCounter, fileCounter) + ".jpg"


def _removeIfEmtpy(dirpath):
    if not os.listdir(dirpath): os.rmdir(dirpath)
