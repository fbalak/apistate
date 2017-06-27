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
            "column": "documented",
            "placement": "end"},
        {"files": glob.glob(os.path.join(
                parser.parse_args().tests, "usmqe", "api", "tendrlapi", "*")),
            "pattern": 'pattern\s*=\s*"',
            "type": "file",
            "column": "covered",
            "placement": "end"},
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
    if source["column"] not in table:
        table[source["column"]] = []

    if source["type"] == "file":
        for file_path in source['files']:
            if os.path.isfile(file_path):
                with open(file_path, 'r') as f:
                    lines = f.readlines()
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
                rows[table[key][i]] = dict.fromkeys(table.keys(), "")
            rows[table[key][i]][key] = "X"
        except:
            pass
for i in list(rows.keys()):
    rows[i]["API state"] = i

print(",".join(rows[next(iter(rows))].keys()[::-1]))
for i in sorted(rows):
    print(",".join(rows[i].values()[::-1]))
