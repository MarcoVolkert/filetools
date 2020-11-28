import csv
import os

__all__ = ["replace"]


def replace(output: str, source_key="PC"):
    csv_filename = "mapping.csv"
    csv.register_dialect('semicolon', delimiter=';', lineterminator='\r\n')
    with open(csv_filename, "r") as csv_file:
        reader = csv.DictReader(csv_file, dialect='semicolon')
        for row in reader:
            for (dirpath, dirnames, filenames) in os.walk(os.getcwd()):
                for filename in filenames:
                    if filename == csv_filename:
                        continue
                    outlines = []
                    with open(filename, "r") as file:
                        for line in file:
                            if not line.startswith('#') and row[source_key] in line:
                                if output == "IPod":
                                    if ".m4a" in line:
                                        line = line.replace(row[source_key], row[output]).replace(".m4a", ".mp3")
                                else:
                                    line = line.replace(row[source_key], row[output])
                            outlines.append(line)
                    with open(filename, "w") as file:
                        file.writelines(outlines)

    outlines = []
    for (dirpath, dirnames, filenames) in os.walk(os.getcwd()):
        for filename in filenames:
            if filename == csv_filename:
                continue
            with open(filename, "r") as file:
                for line in file:
                    if line not in outlines:
                        outlines.append(line)
    with open("Dance.m3u8", "w") as file:
        file.writelines(outlines)
