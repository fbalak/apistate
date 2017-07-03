import argparse
import os
import re
import glob
import requests
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--api', type=str, action="store", required=True,
                    help='Path to tendrl api repository.')
parser.add_argument('--tests', type=str, action="store", required=True,
                    help='Path to tendrl usemqe-tests repository.')


sources = [
        {"files": glob.glob(os.path.join(parser.parse_args().api, "docs", "*")),
            "pattern": 'api/1.0/',
            "type": "file",
            "column": "Documented",
            "z-index": 3,
            "placement": "end"},
        {"files": glob.glob(os.path.join(
                parser.parse_args().tests, "usmqe", "api", "tendrlapi", "*")),
            "pattern": 'pattern\s*=\s*"',
            "type": "file",
            "column": "In QE framework",
            "map_column": "In QE tests",
            "z-index": 4,
            "map_z-index": 5,
            "placement": "end",
            "mapping": "^\s*def (.*?)\(",
            "dict": {},
            "mapsearch":glob.glob(os.path.join(
                parser.parse_args().tests, "usmqe_tests", "api", "*", "*"))},
        ]

aliases = [
        {"pattern": ".{8}-.{4}-.{4}-.{4}-.{12}", "repl": ":id"},
        {"pattern": ":cluster_id:", "repl": ":id"},
        {"pattern": ":cluster_id", "repl": ":id"},
        {"pattern": ":job_id", "repl": ":id"},
        {"pattern": "thardy", "repl": ":id"},
        {"pattern": "{username}", "repl": ":id"},
        {"pattern": "\{\}", "repl": ":id"},
        ]

invalid = ["", ":id/GetVol", "5291c055-70d3-4450-9769-2f6",
           "users/:id----------Sample",
           ":id/CephCreatePoolSample"]

table = {}
imports = []

for source in sources:
    if "z-index" not in source:
        source["z-index"] = 0
    if source["column"] not in table:
        table[source["column"]] = []
    mapitem = None

    if source["type"] == "file":
        if "mapping" in source:
            mapsearch = re.compile(source["mapping"])
        for file_path in source['files']:
            if os.path.isfile(file_path):
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    mapkey = None
                    for i in range(0, len(lines)):
                        try:
                            line = "{}{}{}".format(
                                lines[i],
                                lines[i+1],
                                lines[i+2])
                            line = line.replace("\n", "")
                            run = re.search("run: [a-zA-Z0-9-._]*", line)
                            try:
                                imports.append(line[run.start()+5:run.end()])
                            except:
                                pass
                            for alias in aliases:
                                line = re.sub(
                                    alias["pattern"],
                                    alias["repl"],
                                    line)
                            # print(line)
                            if "mapping" in source:
                                q = mapsearch.search(line)
                                if q:
                                    mapkey = q.group(1)
                                    if mapkey not in source["dict"]:
                                        source["dict"][mapkey] = None
                            p = re.search(source['pattern'], line)
                            if source['placement'] == "begin":
                                url = line[:p.span()[1]]
                                url = url.split('"')[0]
                                url = url.strip().split(' ')[0]\
                                .strip("-").strip("\",")\
                                .strip("'").strip(":")
                            else:
                                url = line[p.span()[1]:].split(' ')[0]\
                                    .strip("-").strip("\",").strip("'")
                                url = url.split('"')[0]
                            try:
                                url = source['prefix']+url
                            except:
                                pass

                            if url not in table[source["column"]]\
                            and url not in invalid:
                                table[source["column"]].append(url)
                                source["dict"][mapkey] = url


                        except Exception as err:
                            pass
        if "dict" in source:
            #print(source["dict"])
            if "map_column" in source:
                table_key = source["map_column"]
            else:
                table_key = "{}_map".format(source["column"])
            table[table_key] = []
            for file_path in source['mapsearch']:
                if os.path.isfile(file_path):
                    with open(file_path, 'r') as f:
                        lines = f.readlines()
                        for line in lines:
                            try:
                                for key in source["dict"]:
                                    url = None
                                    p = re.search("{}\(".format(key), line)
                                    if p:
                                        url = source["dict"][key]
                                    if url not in table[table_key]\
                                    and url not in invalid and url:
                                        table[table_key].append(url)
                                        url = None
                            except Exception as err:
                                pass

    elif source["type"] == "web":
        data = requests.get(source["url"]).json()
        for i in data[source["pattern"]]:
            table[source["column"]].append(i["name"])

    elif source["type"] == "add":
        for i in source["pattern"]:
            table[source["column"]].append(i)


used = {}
rows = []


rows = {}
max_i = max([len(table[x]) for x in table.keys()])
for i in range(0, max_i):
    for key in table.keys():
        try:
            if table[key][i] not in rows:
                rows[table[key][i]] = dict.fromkeys(table.keys(), "No")
            rows[table[key][i]][key] = "Yes"
        except:
            pass


vheader_name = "API state"
for i in list(rows.keys()):
    rows[i][vheader_name] = i

header = rows[next(iter(rows))].keys()
vheader_idx = header.index(vheader_name)
del header[vheader_idx]
z_indexes = [{"column":x, "z-index": 0} for x in header]
for z in z_indexes:
    for source in sources:
        if source["column"] == z["column"] and source["z-index"] is not None:
            z["z-index"] = source["z-index"]
        if "map_column" in source and source["map_column"] == z["column"] and source["map_z-index"] is not None:
            z["z-index"] = source["map_z-index"]
header_sorted =  [x["column"] for x in sorted(z_indexes, key=lambda k: k["z-index"])]
value_indexes = [header_sorted.index(x) for x in header]
print("{},".format(vheader_name) + ",".join(header_sorted))
for i in sorted(rows):
    row_values = rows[i].values()
    vheader_value = row_values.pop(vheader_idx)
    row_values = [x for x in row_values]
    row_values_sorted = [None] * len(row_values)
    for idx, value in zip(value_indexes, row_values):
        row_values_sorted[idx] = value
    print("{},".format(vheader_value) + ",".join(row_values_sorted))
