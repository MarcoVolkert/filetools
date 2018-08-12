#!/usr/bin/env python3

"""
collection of rename operations
"""

__author__ = "Marco Volkert"
__copyright__ = "Copyright 2017, Marco Volkert"
__email__ = "marco.volkert24@gmx.de"
__status__ = "Development"

from compare import are_similar
from natsort import natsorted
import datetime as dt
from collections import OrderedDict
from helpers import *
# for reloading
from IPython import get_ipython

get_ipython().magic('reload_ext autoreload')


def setCounters(name="", start=1, subpath=""):
    inpath = concatPath(subpath)
    if name: inpath += os.path.sep + name
    dirCounter = start
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        if inpath == dirpath: continue
        print(dirpath)
        fileCounter = 1
        filenames = natsorted(filenames)
        for filename in filenames:
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
            dirCounter=setCounters("",dirCounter, dirname)


def normalizeCountersKeepName(subpath="", start=1, write=False, digits=2):
    inpath = concatPath(subpath)
    fileCounter = 1
    lastNameMain = ""
    lastNameMid = ""
    lastdirpath = ""
    matchreg = r"^([-\w +]+)_([ALS]{0,3}[0-9]+)[+]?_([0-9]+)"
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
                    dirCounterDict[nameMain] += 1
                else:
                    dirCounterDict[nameMain] = start
                fileCounter = 1
            elif not nameMid == lastNameMid or not lastdirpath == dirpath:
                dirCounterDict[nameMain] += 1
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
            normalizeCounters(dirname, prefix_name+dirname, 1, write, digits)


def normalizeCountersMulti(name="", write=False, subpath="", digits=2):
    inpath = concatPath(subpath)
    dirCounter = 0
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        if not inpath == dirpath: continue
        for dirname in dirnames:
            dirCounter = normalizeCounters(dirname, name, dirCounter + 1, write, digits)


def normalizeCounters(subpath="", name="", start=1, write=False, digits=2):
    inpath = concatPath(subpath)
    dirCounter = start - 1
    fileCounter = 1
    lastNameMid = ""
    outstring = ""
    matchreg = r"([0-9]+)_([0-9]+)."
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


def normalizeCountersButKeepName(subpath="", name="", start=1, write=False, digits=2):
    inpath = concatPath(subpath)
    dirCounter = start - 1
    normalDirCounter = dirCounter
    fileCounter = 1
    lastNameMain = name
    lastNameMid = ""
    lastdirpath = ""
    matchregName = r"^([-\w +]+)_([ALS]{0,3}[0-9]+)[+]?_([0-9]+)"
    matchreg = r"([0-9]+)_([0-9]+)."
    outstring = ""
    dirCounterDict = dict()
    if write: renameTemp(inpath)
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        filenames = natsorted(filenames)
        print(lastdirpath,dirpath)
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
            if not nameMain == lastNameMain or not nameMid == lastNameMid or not lastdirpath == dirpath:
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


def detectSimilar(pathA, pathB=""):
    if not pathB: pathB = pathA
    filenamesA = getFileNamesOfMainDir(pathA)
    filenamesB = getFileNamesOfMainDir(pathB)

    filenamesB = filenamesB[::-1]
    for filenameA in filenamesA:
        print(filenameA)
        for filenameB in filenamesB:
            if filenameA == filenameB: break
            if not isfile(pathA, filenameA) or not isfile(pathB, filenameB): continue
            if not are_similar((pathA, filenameA), (pathB, filenameB), 0.95): continue
            moveToSubpath(filenameB, pathB, "multiple")


def detectSimilar2(pathA, pathB="", startwith=""):
    if not pathB: pathB = pathA
    filenamesA = getFileNamesOfMainDir(pathA)
    filenamesB = getFileNamesOfMainDir(pathB)

    found = False
    for i, filenameA in enumerate(filenamesA):
        if startwith == filenameA: found = True
        if startwith and not found: continue
        print(filenameA)
        for j, filenameB in enumerate(filenamesB[i + 1:i + 40]):
            if not isfile(pathA, filenameA) or not isfile(pathB, filenameB): continue
            if not are_similar((pathA, filenameA), (pathB, filenameB), 0.95): continue
            moveToSubpath(filenameB, pathB, "multiple")


def detectSimilarSeries(similarity=0.95, checkSameName=True, useSubPath=True, subPath=""):
    def getMainName(nameMid):
        matchreg = r"([-\w +]+)_([0-9]+)"
        match = re.search(matchreg, nameMid)
        if match:
            return match.group(1)
        else:
            return ""

    path = concatPath(subPath)
    filenames = getFileNamesOfMainDir2(path, useSubPath)
    matchreg = r"([-\w +]+)_([0-9]+)."
    moveList = []
    dircounter = 1
    outstring=""
    for i, filenameA in enumerate(filenames):

        if not isfile(*filenameA): continue
        matchA = re.search(matchreg, filenameA[1])
        if not matchA: continue
        namEnd = matchA.group(2)
        if not namEnd == "01": continue
        print("A", filenameA[1])
        lastNameMid = matchA.group(1)
        lastNameMain = getMainName(lastNameMid)
        moveList.append(filenameA)
        for j, filenameB in enumerate(filenames[i + 1:]):
            if not isfile(*filenameA) or not isfile(*filenameB): continue
            matchB = re.search(matchreg, filenameB[1])
            if not matchB: continue
            nameMid = matchB.group(1)
            nameMain = getMainName(nameMid)
            if checkSameName and not nameMain == lastNameMain: break
            namEnd = matchB.group(2)
            if nameMid == lastNameMid:
                print("B", filenameB[1])
                moveList.append(filenameB)
                continue
            if not namEnd == "01": continue
            if not are_similar(filenameA, filenameB, similarity): continue
            print("Bsim", filenameB[1])
            outstring += filenameA[0]+os.path.sep+filenameA[1]+" "+filenameB[0]+os.path.sep+filenameB[1] + "\n"
            moveList.append(filenameB)
            lastNameMid = nameMid

        if not lastNameMid == matchA.group(1):
            dirname = "%03d" % dircounter
            dircounter += 1
            for filename in moveList:
                moveToSubpath(filename[1], filename[0], dirname)
        moveList = []
    writeToFile(path + "\\similar.txt", outstring)


def detectSimilarSeriesPerFolder(similarity=0.95, checkSameName=False, useSubPath=True):
    # from name-surname to Name Surname
    inpath = concatPath("")
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        if not inpath == dirpath: continue
        for dirname in dirnames:
            detectSimilarSeries(similarity, checkSameName, useSubPath, dirname)


def concat_files(concat_filename = "similar.txt"):
    """
    searches for a file named similar.txt in sub directories and writes the content of this
    to a file in the main directory
    """
    inpath = concatPath("")
    outstring = "";
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        if not inpath == dirpath: continue
        for dirname in dirnames:
            filename = dirname + os.sep + concat_filename
            if not os.path.isfile(filename): continue
            ifile = open(filename, "r")
            for line in ifile.readlines():
                outstring += line
            ifile.close()
            os.remove(filename)
    writeToFile(inpath + os.sep + concat_filename, outstring)


def detectSimilarSelfMultiple(subpath=""):
    inpath = concatPath(subpath)
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        if os.path.basename(dirpath) == "multiple": continue
        print(dirpath)
        detectSimilar(dirpath)


def detectSimilar2SelfMultiple(startwith="", subpath=""):
    inpath = concatPath(subpath)
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        if os.path.basename(dirpath) == "multiple": continue
        print(dirpath)
        detectSimilar2(dirpath, startwith=startwith)


def deleteNewNamesTxt(subpath=""):
    inpath = concatPath(subpath)
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        filename = dirpath + "\\newNames.txt"
        if not os.path.isfile(filename): continue
        os.remove(filename)


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


def _fixInitialNotNaturalSorting(dirpath, lastNameMid, series, write):
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


def findSameNames():
    inpath = concatPath("")
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
    writeToFile(inpath + "\\sameNames.txt", outstring)
