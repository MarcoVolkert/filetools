#!/usr/bin/env python3

"""
collection of rename operations
"""
from typing import Iterable

__author__ = "Marco Volkert"
__copyright__ = "Copyright 2017, Marco Volkert"
__email__ = "marco.volkert24@gmx.de"
__status__ = "Development"

import datetime as dt

from .helpers import *

file_types = (".JPG", ".jpg", ".tif", ".tiff", ".hdr", ".exr", ".ufo", ".fpx", ".RW2", ".Raw")

__all__ = ["setCounters", "setCountersMulti", "setCountersMulti2", "normalizeCounters", "normalizeCountersButKeepName",
           "normalizeCountersKeepName", "normalizeCountersMulti", "normalizeCountersMultiDirname", "foldersToUpper",
           "renameTempBack", "renameTempBackAll", "fixInitialNotNaturalSorting"]


def setCounters(name="", start=1, subpath="") -> int:
    inpath = concatPath(subpath)
    if name: inpath += os.path.sep + name
    dirCounter = start
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        if inpath == dirpath: continue
        print(dirpath)
        fileCounter = 1
        filenames = natsorted(filenames)
        for filename in filenames:
            if not _file_has_ext(filename, file_types):
                continue
            newFilename = getNewName(name, dirCounter, fileCounter)
            os.rename(os.path.join(dirpath, filename), os.path.join(inpath, newFilename))
            fileCounter += 1
        if filenames: dirCounter += 1
        removeIfEmtpy(dirpath)
    return dirCounter


def setCountersMulti(subpath=""):
    inpath = concatPath(subpath)
    foldersToUpper(True, subpath)
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        if not inpath == dirpath: continue
        print(dirpath)
        for dirname in dirnames:
            setCounters(dirname, subpath=subpath)


def setCountersMulti2(start=1):
    inpath = concatPath("")
    dirCounter = start
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        if not inpath == dirpath: continue
        print(dirpath)
        for dirname in dirnames:
            dirCounter = setCounters("", dirCounter, dirname)


def normalizeCountersKeepName(subpath="", start=1, write=False, digits=2, increment=1):
    inpath = concatPath(subpath)
    fileCounter = 1
    lastNameMain = ""
    lastNameMid = ""
    lastdirpath = ""
    matchreg = r"^([-\w +]+)_([A-Z]{0,3}[0-9]+)[+]?_([0-9]+)"
    outstring = ""
    dirCounterDict = dict()
    if write: renameTemp(inpath)
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        filenames = natsorted(filenames)
        for filename in filenames:
            match = re.search(matchreg, filename)
            if not match:
                print("no match", dirpath, filename)
                if write: renameTempBack(dirpath, filename)
                continue
            nameMain = match.group(1)
            nameMid = match.group(2)
            if not nameMain == lastNameMain:
                if nameMain in dirCounterDict:
                    dirCounterDict[nameMain] += increment
                else:
                    dirCounterDict[nameMain] = start
                fileCounter = 1
            elif not nameMid == lastNameMid or not lastdirpath == dirpath:
                dirCounterDict[nameMain] += increment
                fileCounter = 1
            else:
                fileCounter += 1
            newFilename = getNewName(nameMain, dirCounterDict[nameMain], fileCounter, digits)
            if write:
                renameInPlace(dirpath, filename, newFilename)
            elif not filename == newFilename:
                outstring += filename + "\t" + newFilename + "\n"
            lastNameMain = nameMain
            lastNameMid = nameMid
            lastdirpath = dirpath
    if not write: writeToFile(inpath + "\\newNames.txt", outstring)


def normalizeCountersMultiDirname(prefix_name="", write=False, subpath="", digits=2):
    inpath = concatPath(subpath)
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        if not inpath == dirpath: continue
        for dirname in dirnames:
            print("renameIndexNorm2Multi:", dirname)
            normalizeCounters(dirname, prefix_name + dirname, 1, write, digits)


def normalizeCountersMulti(name="", write=False, subpath="", digits=2):
    inpath = concatPath(subpath)
    dirCounter = 0
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        if not inpath == dirpath: continue
        for dirname in dirnames:
            dirCounter = normalizeCounters(dirname, name, dirCounter + 1, write, digits)


def normalizeCounters(subpath="", name="", start=1, write=False, digits=2) -> int:
    inpath = concatPath(subpath)
    dirCounter = start - 1
    fileCounter = 1
    lastNameMid = ""
    outstring = ""
    matchreg = r"([0-9]+)(?:_|-)([0-9]+)."
    if write: renameTemp(inpath)
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        print("renameIndexNorm2:", dirpath)
        filenames = natsorted(filenames)
        for filename in filenames:

            match = re.search(matchreg, filename)
            if not match:
                print("no match", dirpath, filename)
                if write: renameTempBack(dirpath, filename)
                continue
            nameMid = match.group(1)
            if not nameMid == lastNameMid:
                dirCounter += 1
                fileCounter = 1
            else:
                fileCounter += 1
            newFilename = getNewName(name, dirCounter, fileCounter, digits)
            if write:
                renameInPlace(dirpath, filename, newFilename)
            elif not filename == newFilename:
                outstring += filename + "\t" + newFilename + "\n"
            lastNameMid = nameMid
    if not write: writeToFile(inpath + "\\newNames.txt", outstring)
    return dirCounter


def normalizeCountersButKeepName(subpath="", name="", start=1, write=False, digits=2, new_on_dirchange=True):
    inpath = concatPath(subpath)
    dirCounter = start - 1
    normalDirCounter = dirCounter
    fileCounter = 1
    lastNameMain = name
    lastNameMid = ""
    lastdirpath = ""
    matchregName = r"^([-\w +]+)_([A-Z]{0,3}[0-9]+)[+]?_([0-9]+)"
    matchreg = r"([0-9]+)_([0-9]+)."
    outstring = ""
    dirCounterDict = dict()
    if write: renameTemp(inpath)
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        filenames = natsorted(filenames)
        print(lastdirpath, dirpath)
        for filename in filenames:
            matchName = re.search(matchregName, filename)
            match = re.search(matchreg, filename)
            if matchName:
                nameMain = matchName.group(1)
                nameMid = matchName.group(2)
                if not nameMain == lastNameMain:
                    dirCounter = dirCounterDict.setdefault(nameMain, 0)
            elif match:
                nameMain = name
                nameMid = match.group(1)
                if not nameMain == lastNameMain:
                    dirCounter = normalDirCounter
            else:
                print("no match", dirpath, filename)
                if write: renameTempBack(dirpath, filename)
                continue
            if not nameMain == lastNameMain or not nameMid == lastNameMid or (
                    new_on_dirchange and not lastdirpath == dirpath):
                dirCounter += 1
                fileCounter = 1
            else:
                fileCounter += 1
            if not matchName and match:
                normalDirCounter = dirCounter
            else:
                dirCounterDict[nameMain] = dirCounter
            newFilename = getNewName(nameMain, dirCounter, fileCounter, digits)

            if write:
                renameInPlace(dirpath, filename, newFilename)
            elif not filename == newFilename:
                outstring += filename + "\t" + newFilename + "\n"
            lastNameMain = nameMain
            lastNameMid = nameMid
            lastdirpath = dirpath
    if not write: writeToFile(inpath + "\\newNames.txt", outstring)
    return normalDirCounter


def foldersToUpper(write=True, subpath=""):
    # from name-surname to Name Surname
    inpath = concatPath(subpath)
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
            if write: renameInPlace(dirpath, dirname, newName)


def renameTempBackAll():
    inpath = concatPath("")
    matchreg = renameTemp.temppostfix + '$'
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        for filename in filenames:
            match = re.search(matchreg, filename)
            if not match: continue
            newFilename = re.sub(matchreg, '', filename)
            renameInPlace(dirpath, filename, newFilename)


def fixInitialNotNaturalSorting(write=False, year=2017, month=12, day=20, subpath=""):
    inpath = concatPath(subpath)
    lastNameMid = ""
    matchreg = r"([-\w +]+)_([0-9]+)."
    matchdate = dt.datetime(year, month, day)
    temp = ""
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        series = []
        for filename in filenames:
            fullname = dirpath + "\\" + filename
            modified = dt.datetime.fromtimestamp(os.path.getmtime(fullname))
            if modified < matchdate: continue
            match = re.search(matchreg, filename)
            if not match: continue
            nameMid = match.group(1)
            if not nameMid == lastNameMid:
                _fixInitialNotNaturalSorting(dirpath, lastNameMid, series, write)
                series = []
            if write: temp = renameTempSingle(dirpath, filename)
            series.append(filename + temp)
            lastNameMid = nameMid
        _fixInitialNotNaturalSorting(dirpath, lastNameMid, series, write)


def _fixInitialNotNaturalSorting(dirpath: str, lastNameMid: str, series: List[str], write: bool):
    if len(series) < 10:
        for name in series:
            if write: renameTempBack(dirpath, name)
        return
    # series = series[0:1] + series[-8:] + series[1:-8]
    # series = series[0:1] + series[-1:] + series[2:-1] + series[1:2] #switch 2 and end
    series = series[0:2] + series[-1:] + series[2:-1]  # put end to 3
    for i, name in enumerate(series, start=1):
        newname = lastNameMid + "_%02d.jpg" % i
        print(name, newname)
        if write: renameInPlace(dirpath, name, newname)


def _file_has_ext(filename: str, file_extensions: Iterable, ignore_case=True) -> bool:
    for fileext in file_extensions:
        if ignore_case:
            fileext = fileext.lower()
            filename = filename.lower()
        if fileext == filename[filename.rfind("."):]:
            return True
    return False
