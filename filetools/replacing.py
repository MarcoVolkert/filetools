import csv
import os


def replace(reverse=False):
    csv_filename = "mapping.csv"
    csv.register_dialect('semicolon', delimiter=';', lineterminator='\r\n')
    with open(csv_filename, "r") as csv_file:
        reader = csv.reader(csv_file, dialect='semicolon')
        for row in reader:
            old, new = row[:2]
            if reverse:
                new, old = old, new
            for (dirpath, dirnames, filenames) in os.walk(os.getcwd()):
                for filename in filenames:
                    if filename == csv_filename:
                        continue
                    outlines = []
                    with open(filename, "r") as file:
                        for line in file:
                            if not line.startswith('#'):
                                line = line.replace(old, new)
                            outlines.append(line)
                    with open(filename, "w") as file:
                        file.writelines(outlines)


