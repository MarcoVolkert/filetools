import os
import re


def renameInPlace(dirpath, oldFilename, newFilename):
    os.rename(dirpath + "\\" + oldFilename, dirpath + "\\" + newFilename)


def renameTemp(inpath):
    if not os.path.isdir(inpath):
        print('not found directory: ' + inpath)
        return
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        for filename in filenames:
            renameInPlace(dirpath, filename, filename + renameTemp.temppostfix)
    return renameTemp.temppostfix


renameTemp.temppostfix = "temp"


def renameTempSingle(dirpath, filename):
    renameInPlace(dirpath, filename, filename + renameTemp.temppostfix)
    return renameTemp.temppostfix


def renameTempBack(dirpath, filename):
    newFilename = re.sub(renameTemp.temppostfix + '$', '', filename)
    renameInPlace(dirpath, filename, newFilename)


def concatPath(subpath):
    if not subpath == "": subpath = "\\" + subpath
    fullpath = os.getcwd() + subpath
    if not os.path.isdir(fullpath):
        print(fullpath, "is not a valid path")
    else:
        print(fullpath)
    return fullpath


def getNewName(name, dirCounter, fileCounter, digits=2):
    if name: name += "_"
    return name + ("%0" + str(digits) + "d_%02d") % (dirCounter, fileCounter) + ".jpg"


def removeIfEmtpy(dirpath):
    if not os.listdir(dirpath): os.rmdir(dirpath)


def writeToFile(path, content):
    ofile = open(path, 'w')
    ofile.write(content)
    ofile.close()


def moveToSubpath(filename, dirpath, subpath):
    os.makedirs(dirpath + "\\" + subpath, exist_ok=True)
    if not os.path.isfile(dirpath + "\\" + filename): return
    os.rename(dirpath + "\\" + filename, dirpath + "\\" + subpath + "\\" + filename)


def getFileNamesOfMainDir(path):
    for (dirpath, dirnames, filenames) in os.walk(path):
        return [filename for filename in filenames if ".jpg" in filename]


def isfile(*path):
    return os.path.isfile(os.path.join(*path))