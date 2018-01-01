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
from compare import are_similar
from natsort import natsorted
import datetime as dt
from collections import OrderedDict
# for reloading
from IPython import get_ipython

get_ipython().magic('reload_ext autoreload')


def setCounters(name="", start=1, subpath=""):
    inpath = _concatPath(subpath) + "\\" + name
    dirCounter = start
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        if inpath == dirpath: continue
        print(dirpath)
        fileCounter = 1
        filenames = natsorted(filenames)
        for filename in filenames:
            newFilename = _getNewName(name, dirCounter, fileCounter)
            os.rename(dirpath + "\\" + filename, inpath + "\\" + newFilename)
            fileCounter += 1
        if filenames: dirCounter += 1
        _removeIfEmtpy(dirpath)


def setCountersMulti(subpath=""):
    inpath = _concatPath(subpath)
    foldersToUpper(True, subpath)
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        if not inpath == dirpath: continue
        print(dirpath)
        for dirname in dirnames:
            setCounters(dirname, subpath=subpath)


def normalizeCountersKeepName(subpath="", start=1, write=False, digits=2):
    inpath = _concatPath(subpath)
    fileCounter = 1
    lastNameMain = ""
    lastNameMid = ""
    lastdirpath = ""
    matchreg = r"^([-\w +]+)_([ALS]{0,3}[0-9]+)_([0-9]+)"
    outstring = ""
    dirCounterDict = dict()
    if write: _renameTemp(inpath)
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        filenames = natsorted(filenames)
        for filename in filenames:
            match = re.search(matchreg, filename)
            if not match:
                print("no match", dirpath, filename)
                if write: _renameTempBack(dirpath, filename)
                continue
            nameMain = match.group(1)
            nameMid = match.group(2)
            if not nameMain == lastNameMain:
                if nameMain in dirCounterDict:
                    dirCounterDict[nameMain] += 1
                else:
                    dirCounterDict[nameMain] = start
                fileCounter = 1
            elif not nameMid == lastNameMid or not lastdirpath == dirpath:
                dirCounterDict[nameMain] += 1
                fileCounter = 1
            else:
                fileCounter += 1
            newFilename = _getNewName(nameMain, dirCounterDict[nameMain], fileCounter, digits)
            outstring += newFilename + "\n"
            if write: _renameInPlace(dirpath, filename, newFilename)
            lastNameMain = nameMain
            lastNameMid = nameMid
            lastdirpath = dirpath
    if not write: _writeToFile(inpath + "\\newNames.txt", outstring)


def normalizeCountersMultiDirname(write=False, subpath="", digits=2):
    inpath = _concatPath(subpath)
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        if not inpath == dirpath: continue
        for dirname in dirnames:
            print("renameIndexNorm2Multi:", dirname)
            normalizeCounters(dirname, dirname, 1, write, digits)


def normalizeCountersMulti(name="", write=False, subpath="", digits=2):
    inpath = _concatPath(subpath)
    dirCounter = 0
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        if not inpath == dirpath: continue
        for dirname in dirnames:
            dirCounter = normalizeCounters(dirname, name, dirCounter + 1, write, digits)


def normalizeCounters(subpath="", name="", start=1, write=False, digits=2):
    inpath = _concatPath(subpath)
    dirCounter = start - 1
    fileCounter = 1
    lastNameMid = ""
    matchreg = r"([0-9]+)_([0-9]+)."
    if write: _renameTemp(inpath)
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        print("renameIndexNorm2:", dirpath)
        filenames = natsorted(filenames)
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
            newFilename = _getNewName(name, dirCounter, fileCounter, digits)
            print(dirpath, newFilename)
            if write: _renameInPlace(dirpath, filename, newFilename)
            lastNameMid = nameMid
    return dirCounter


def normalizeCountersButKeepName(subpath="", name="", start=1, write=False, digits=2):
    inpath = _concatPath(subpath)
    dirCounter = start - 1
    normalDirCounter = dirCounter
    fileCounter = 1
    lastNameMain = name
    lastNameMid = ""
    lastdirpath = ""
    matchregName = r"^([-\w +]+)_([0-9]+)[+]?_([0-9]+)"
    matchreg = r"([0-9]+)_([0-9]+)."
    outstring = ""
    dirCounterDict = dict()
    if write: _renameTemp(inpath)
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        filenames = natsorted(filenames)
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
                if write: _renameTempBack(dirpath, filename)
                continue
            if not nameMid == lastNameMid or not lastdirpath == dirpath:
                dirCounter += 1
                fileCounter = 1
            else:
                fileCounter += 1
            if not matchName and match:
                normalDirCounter = dirCounter
            else:
                dirCounterDict[nameMain] = dirCounter
            newFilename = _getNewName(nameMain, dirCounter, fileCounter, digits)

            if write:
                _renameInPlace(dirpath, filename, newFilename)
            else:
                outstring += filename + "\t" + newFilename + "\n"
            lastNameMain = nameMain
            lastNameMid = nameMid
            lastdirpath = dirpath
    if not write: _writeToFile(inpath + "\\newNames.txt", outstring)
    return normalDirCounter


def foldersToUpper(write=True, subpath=""):
    # from name-surname to Name Surname
    inpath = _concatPath(subpath)
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


def _renameTempSingle(dirpath, filename):
    _renameInPlace(dirpath, filename, filename + _renameTemp.temppostfix)
    return _renameTemp.temppostfix


def _renameTempBack(dirpath, filename):
    newFilename = re.sub(_renameTemp.temppostfix + '$', '', filename)
    _renameInPlace(dirpath, filename, newFilename)


def _concatPath(subpath):
    if not subpath == "": subpath = "\\" + subpath
    fullpath = os.getcwd() + subpath
    if not os.path.isdir(fullpath):
        print(fullpath, "is not a valid path")
    else:
        print(fullpath)
    return fullpath


def _getNewName(name, dirCounter, fileCounter, digits=2):
    if name: name += "_"
    return name + ("%0" + str(digits) + "d_%02d") % (dirCounter, fileCounter) + ".jpg"


def _removeIfEmtpy(dirpath):
    if not os.listdir(dirpath): os.rmdir(dirpath)


def _writeToFile(path, content):
    ofile = open(path, 'w')
    ofile.write(content)
    ofile.close()


def _moveToSubpath(filename, dirpath, subpath):
    os.makedirs(dirpath + "\\" + subpath, exist_ok=True)
    if not os.path.isfile(dirpath + "\\" + filename): return
    os.rename(dirpath + "\\" + filename, dirpath + "\\" + subpath + "\\" + filename)


def detectSimilar(pathA, pathB=""):
    if not pathB: pathB = pathA
    filenamesA = []
    filenamesB = []
    for (dirpath, dirnames, filenames) in os.walk(pathA):
        if not pathA == dirpath: break
        filenamesA = [filename for filename in filenames if ".jpg" in filename]
    for (dirpath, dirnames, filenames) in os.walk(pathB):
        if not pathB == dirpath: break
        filenamesB = [filename for filename in filenames if ".jpg" in filename]

    filenamesB = filenamesB[::-1]
    for filenameA in filenamesA:
        print(filenameA)
        for filenameB in filenamesB:
            if filenameA == filenameB: break
            if not os.path.isfile(pathA + "\\" + filenameA): continue
            if not os.path.isfile(pathB + "\\" + filenameB): continue
            if not are_similar(pathA + "\\" + filenameA, pathB + "\\" + filenameB, 0.95): continue
            _moveToSubpath(filenameB, pathB, "multiple")


def detectSimilar2(pathA, pathB="", startwith=""):
    if not pathB: pathB = pathA
    filenamesA = []
    filenamesB = []
    for (dirpath, dirnames, filenames) in os.walk(pathA):
        if not pathA == dirpath: break
        filenamesA = [filename for filename in filenames if ".jpg" in filename]
    for (dirpath, dirnames, filenames) in os.walk(pathB):
        if not pathB == dirpath: break
        filenamesB = [filename for filename in filenames if ".jpg" in filename]

    found = False
    for i, filenameA in enumerate(filenamesA):
        if startwith == filenameA: found = True
        if startwith and not found: continue
        print(filenameA)
        for j, filenameB in enumerate(filenamesB[i + 1:i + 40]):
            if not os.path.isfile(pathA + "\\" + filenameA): continue
            if not os.path.isfile(pathB + "\\" + filenameB): continue
            if not are_similar(pathA + "\\" + filenameA, pathB + "\\" + filenameB, 0.95): continue
            _moveToSubpath(filenameB, pathB, "multiple")


def detectSimilarSelfMultiple(subpath=""):
    inpath = _concatPath(subpath)
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        if os.path.basename(dirpath) == "multiple": continue
        print(dirpath)
        detectSimilar(dirpath)


def detectSimilar2SelfMultiple(startwith="", subpath=""):
    inpath = _concatPath(subpath)
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        if os.path.basename(dirpath) == "multiple": continue
        print(dirpath)
        detectSimilar2(dirpath, startwith=startwith)


def deleteNewNamesTxt(subpath=""):
    inpath = _concatPath(subpath)
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        filename = dirpath + "\\newNames.txt"
        if not os.path.isfile(filename): continue
        os.remove(filename)


def renameTempBackAll():
    inpath = _concatPath("")
    matchreg = _renameTemp.temppostfix + '$'
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        for filename in filenames:
            match = re.search(matchreg, filename)
            if not match: continue
            newFilename = re.sub(matchreg, '', filename)
            _renameInPlace(dirpath, filename, newFilename)


def fixInitialNotNaturalSorting(write=False, year=2017, month=12, day=20, subpath=""):
    inpath = _concatPath(subpath)
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
            if write: temp = _renameTempSingle(dirpath, filename)
            series.append(filename + temp)
            lastNameMid = nameMid
        _fixInitialNotNaturalSorting(dirpath, lastNameMid, series, write)


def _fixInitialNotNaturalSorting(dirpath, lastNameMid, series, write):
    if len(series) < 10:
        for name in series:
            if write: _renameTempBack(dirpath, name)
        return
    # series = series[0:1] + series[-8:] + series[1:-8]
    # series = series[0:1] + series[-1:] + series[2:-1] + series[1:2] #switch 2 and end
    series = series[0:2] + series[-1:] + series[2:-1]  # put end to 3
    for i, name in enumerate(series, start=1):
        newname = lastNameMid + "_%02d.jpg" % i
        print(name, newname)
        if write: _renameInPlace(dirpath, name, newname)


def findSameNames():
    inpath = _concatPath("")
    fileDict = OrderedDict()
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        for filename in filenames:
            fileDict.setdefault(filename, [])
            fileDict[filename].append(dirpath)

    outstring = ""
    for filename in fileDict:
        if len(fileDict[filename]) == 1: continue
        outstring += filename
        for dirpath in fileDict[filename]:
            outstring += "\t" + dirpath
        outstring += "\n"
    _writeToFile(inpath + "\\sameNames.txt", outstring)
