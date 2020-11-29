import csv
import os

__all__ = ["replace_playlists"]

from typing import List, Union, OrderedDict, Dict


def replace_playlists(output: str, source_key="PC"):
    cwd = os.getcwd()
    out_dir = os.path.join(cwd, output)
    os.makedirs(out_dir, exist_ok=True)
    all_lines = []
    csv_filename = "mapping.csv"
    mapping_rows = _read_mapping(csv_filename)
    for (dirpath, dirnames, filenames) in os.walk(cwd):
        if not dirpath == cwd:
            break
        for filename in filenames:
            if filename == csv_filename:
                continue
            outlines = []
            with open(filename, "r") as file:
                for line in file:
                    if not line.startswith('#'):
                        for row in mapping_rows:
                            if row[source_key] in line:
                                if output == "IPod":
                                    if ".m4a" in line:
                                        line = line.replace(row[source_key], row[output]).replace(".m4a", ".mp3")
                                else:
                                    line = line.replace(row[source_key], row[output])
                    outlines.append(line)
                    all_lines.append(line)
            with open(os.path.join(out_dir, filename), "w") as file:
                file.writelines(outlines)

    with open(os.path.join(output, "combined.m3u8"), "w") as file:
        file.writelines(all_lines)


def _read_mapping(csv_filename: str) -> List[Union[Dict[str, str], OrderedDict[str, str]]]:
    csv.register_dialect('semicolon', delimiter=';', lineterminator='\r\n')
    with open(csv_filename, "r") as csv_file:
        reader = csv.DictReader(csv_file, dialect='semicolon')
        return [row for row in reader]
