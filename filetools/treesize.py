import csv
import os
from collections import OrderedDict
from typing import List


def writeDirsAndFiles():
    inpath = os.getcwd()
    dicts: List[OrderedDict] = []
    for (dirpath, dirnames, filenames) in os.walk(inpath):
        for filename in filenames:
            stats = os.stat(dirpath + os.sep + filename)
            file_data = OrderedDict()
            file_data["path"] = dirpath
            file_data["name"] = filename
            file_data["isDir"] = False
            file_data["size"] = stats.st_size
            file_data["depth"] = len(dirpath.split(os.sep)) + 1
            dicts.append(file_data)
        for dirname in dirnames:
            stats = os.stat(dirpath + os.sep + dirname)
            file_data = OrderedDict()
            file_data["path"] = dirpath
            file_data["name"] = dirname
            file_data["isDir"] = True
            file_data["size"] = stats.st_size
            file_data["depth"] = len(dirpath.split(os.sep))
            dicts.append(file_data)

    writeCsvFile(dicts)


def writeCsvFile(dicts: List[OrderedDict]):
    csv_filename = "treeSize.csv"
    csv.register_dialect('semicolon', delimiter=';', lineterminator='\n')
    with open(csv_filename, "w", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, ["path", "name", "isDir", "size", "depth"], dialect='semicolon')
        writer.writeheader()
        writer.writerows(dicts)