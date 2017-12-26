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
# for reloading
from IPython import get_ipython

get_ipython().magic('reload_ext autoreload')

print('loaded collection of rename operations')


def setCounters(name="", start=1, subpath=""):
    inpath = _concatPath(setCounters.path, subpath) + "\\" + name
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


def normalizeCountersKeepName(subpath="", start=1, write=False):
    inpath = _concatPath(normalizeCountersKeepName.path, subpath)
    dirCounter = start
    fileCounter = 1
    lastNameMain = ""
    lastNameMid = ""
    matchreg = r"^([-\w +]+)_([ALS]{0,3}[0-9]+)_([0-9]+)"
    outstring = ""
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
                dirCounter = start
                fileCounter = 1
            elif not nameMid == lastNameMid:
                dirCounter += 1
                fileCounter = 1
            else:
                fileCounter += 1
            newFilename = _getNewName(nameMain, dirCounter, fileCounter)
            outstring += newFilename + "\n"
            if write: _renameInPlace(dirpath, filename, newFilename)
            lastNameMain = nameMain
            lastNameMid = nameMid
    if not write: _writeToFile(inpath + "\\newNames.txt", outstring)


normalizeCountersKeepName.path = "F:\\Video\\z_Bearbeitung\\Bilder\\websites\\Amour Angels\\namesFolders\\Tina"


def normalizeCountersMultiDirname(subpath="", write=False):
    inpath = _concatPath(normalizeCountersButKeepName.path, subpath)
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        if not inpath == dirpath: continue
        for dirname in dirnames:
            print("renameIndexNorm2Multi:", dirname)
            normalizeCountersButKeepName(dirname, dirname, 1, write)


def normalizeCountersMulti(subpath="", name="", write=False):
    inpath = _concatPath(normalizeCounters.path, subpath)
    dirCounter = 0
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        if not inpath == dirpath: continue
        for dirname in dirnames:
            dirCounter = normalizeCounters(dirname, name, dirCounter + 1, write)


def normalizeCounters(subpath="", name="", start=1, write=False):
    inpath = _concatPath(normalizeCounters.path, subpath)
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
            newFilename = _getNewName(name, dirCounter, fileCounter)
            print(dirpath, newFilename)
            if write: _renameInPlace(dirpath, filename, newFilename)
            lastNameMid = nameMid
    return dirCounter


normalizeCounters.path = "F:\\Video\\z_Bearbeitung\\new\\photoseries"


def normalizeCountersButKeepName(subpath="", name="", start=1, write=False):
    inpath = _concatPath(normalizeCountersButKeepName.path, subpath)
    dirCounter = start - 1
    normalDirCounter = dirCounter
    fileCounter = 1
    lastNameMain = name
    lastNameMid = ""
    matchregName = r"^([-\w +]+)_([0-9]+)_([0-9]+)"
    matchreg = r"([0-9]+)_([0-9]+)."
    outstring = ""
    if write: _renameTemp(inpath)
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        filenames = natsorted(filenames)
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
            # print(newFilename)
            outstring += filename + "\t" + newFilename + "\n"
            if write: _renameInPlace(dirpath, filename, newFilename)
            lastNameMain = nameMain
            lastNameMid = nameMid
    _writeToFile(inpath + "\\newNames.txt", outstring)


normalizeCountersButKeepName.path = "F:\\Video\\z_Bearbeitung\\Bilder\\sorted\\best"


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
    if not os.path.isdir(fullpath):
        print(fullpath, "is not a valid path")
    else:
        print(fullpath)
    return fullpath


def _getNewName(name, dirCounter, fileCounter):
    if name: name += "_"
    return name + "%02d_%02d" % (dirCounter, fileCounter) + ".jpg"


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
        for filenameB in filenamesB:
            if filenameA == filenameB: break
            if not os.path.isfile(pathA + "\\" + filenameA): continue
            if not os.path.isfile(pathB + "\\" + filenameB): continue
            if not are_similar(pathA + "\\" + filenameA, pathB + "\\" + filenameB, 0.95): continue
            _moveToSubpath(filenameB, pathB, "multiple")


def detectSimilarSelfMultiple(path):
    for (dirpath, dirnames, filenames) in os.walk(path):
        if os.path.basename(dirpath) == "multiple": continue
        print(dirpath)
        detectSimilar(dirpath)


def deleteNewNamesTxt(inpath):
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        filename = dirpath + "\\newNames.txt"
        if not os.path.isfile(filename): continue
        os.remove(filename)


def fixInitialNotNaturalSorting(inpath, write=False):
    lastNameMid = ""
    matchreg = r"([-\w +]+)_([0-9]+)."
    if write: _renameTemp(inpath)
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        series = []
        for filename in filenames:
            print(filename)
            match = re.search(matchreg, filename)
            if not match:
                if write: _renameTempBack(dirpath, filename)
                continue
            nameMid = match.group(1)
            if not nameMid == lastNameMid:
                series = series[0:1] + series[-8:] + series[1:-8]
                for i, name in enumerate(series, start=1):
                    newname = lastNameMid + "_%2d.jpg" % i
                    print(name, newname)
                    if write: _renameInPlace(dirpath, name, newname)
                series = []
            else:
                series.append(filename)
            lastNameMid = nameMid
