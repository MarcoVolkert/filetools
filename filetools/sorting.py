#!/usr/bin/env python3

"""
collection of sorting operations
"""

__author__ = "Marco Volkert"
__copyright__ = "Copyright 2017, Marco Volkert"
__email__ = "marco.volkert24@gmx.de"
__status__ = "Development"

import shutil
from collections import OrderedDict

from .compare import are_similar
from .helpers import *

__all__ = ["detectSimilar", "detectSimilar2", "detectSimilarSeries", "detectSimilar2SelfMultiple",
           "detectSimilarSelfMultiple", "detectSimilarSeriesPerFolder", "deleteNewNamesTxt", "findSameNames"]


def detectSimilar(pathA: str, pathB=""):
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


def detectSimilar2(pathA: str, pathB="", startwith=""):
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
    outstring = ""
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
            outstring += filenameA[0] + os.path.sep + filenameA[1] + " " + filenameB[0] + os.path.sep + filenameB[
                1] + "\n"
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
    inpath = concatPath("")
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        if not inpath == dirpath: continue
        for dirname in dirnames:
            detectSimilarSeries(similarity, checkSameName, useSubPath, dirname)


def concat_files(concat_filename="similar.txt"):
    """
    searches for a file named similar.txt in sub directories and writes the content of this
    to a file in the main directory
    """
    inpath = concatPath("")
    outstring = ""
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


def delete_empty_dirs(subpath="", ignored_extensions: List[str] = None):
    inpath = concatPath(subpath)
    for (dirpath, dirnames, filenames) in os.walk(inpath, topdown=False):
        if ignored_extensions:
            filenames = [filename for filename in filenames
                         if not any(filename.endswith(ignored_extension) for ignored_extension in ignored_extensions)]
        dirnames = [dirname for dirname in dirnames if os.path.exists(os.path.join(dirpath, dirname))]
        if not filenames and not dirnames:
            shutil.rmtree(dirpath)


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
