import csv
import os
from typing import List, Union, OrderedDict, Dict

from pydub import AudioSegment
from pydub.utils import mediainfo

__all__ = ["replace_playlists"]


def replace_playlists(output: str, source_key="PC", encoding='latin', convert=True):
    """
    prepare playlist for different destination
    :param output:
        column for output destination
    :param source_key:
        valid path on PC where this is executed
    :param encoding:
        system encoding in case of umlaute
    :param convert:
        optional feature to convert to mp3 if output is old IPod
        see: https://github.com/jiaaro/pydub
        download: https://www.gyan.dev/ffmpeg/builds/
        put into path in start script: os.environ["PATH"] += os.pathsep + r"C:\Program Files\ffmpeg\bin"
    :return:
    """
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
                        name_org = line.strip()
                        if os.path.isfile(name_org.encode(encoding)):
                            for row in mapping_rows:
                                if row[source_key] in line:
                                    if output == "IPod":
                                        if ".m4a" in line:
                                            line = line.replace(row[source_key], row[output]).replace(".m4a", ".mp3")
                                            line_stripped = line.strip()
                                            if convert and not os.path.isfile(line_stripped.encode(encoding)):
                                                print("convert to mp3: ", line_stripped.encode(encoding))
                                                org_version = AudioSegment.from_file(name_org, "m4a")
                                                org_version.export(line_stripped, format="mp3", bitrate="320k",
                                                                   tags=mediainfo(name_org)['TAG'])
                                    else:
                                        line = line.replace(row[source_key], row[output])
                        else:
                            print('warning - does not exist: ', filename, name_org.encode(encoding))
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
