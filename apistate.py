import os
import re
import glob
import requests

sources = [
        {"files": glob.glob('../api/docs/*'),
            "pattern": 'api/1.0/',
            "type": "file",
            "column": "documented",
            "placement": "end"},
        {"files": glob.glob('../api/*'),
            "pattern": 'get \'/',
            "type": "file",
            "column": "implemented",
            "placement": "end"},
        {"files": glob.glob('../usmqe-tests/usmqe/api/tendrlapi/*'),
            "pattern": '(P|p)attern: *"',
            "type": "file",
            "column": "covered",
            "placement": "end"},
        {"files": glob.glob('../gluster-integration/tendrl/gluster_integration/objects/definition/gluster.py'),
            "pattern": '[a-zA-Z0-9]+: +atoms: +- ',
            "type": "file",
            "column": "flows",
            "placement": "begin"},
        {"files": glob.glob('../ceph-integration/tendrl/ceph_integration/objects/definition/ceph.py'),
            "pattern": '[a-zA-Z0-9]+: +atoms: +- ',
            "type": "file",
            "column": "flows",
            "placement": "begin"}
        ]

aliases = [
        {"pattern": ".{8}-.{4}-.{4}-.{4}-.{12}", "repl": ":integration_id"},
        {"pattern": ":cluster_id:", "repl": ":integration_id"},
        {"pattern": ":job_id", "repl": ":integration_id"},
        ]


table = {}

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
                            for alias in aliases:
                                line = re.sub(
                                    alias["pattern"],
                                    alias["repl"],
                                    line)
                            # print(line)
                            p = re.search(source['pattern'], line)
                            if source['placement'] == "begin":
                                url = line[:p.span()[1]]
                                url = re.sub('^ {8}', ":integration_id/", url)
                                url = url.strip().split(' ')[0]\
                                    .strip("-").strip("\",").strip("'").strip(":")
                            else:
                                url = line[p.span()[1]:].split(' ')[0]\
                                    .strip("-").strip("\",").strip("'")

                            # print("{}".format(url))
                            if url not in table[source["column"]]:
                                table[source["column"]].append(url)
                                # print(line)
                        except Exception as err:
                            # print("{}".format(err))
                            pass

    elif source["type"] == "web":
        data = requests.get(source["url"]).json()
        for i in data[source["pattern"]]:
            table[source["column"]].append(i["name"])


used = {}
rows = []


rows = {}
max_i = max([len(table[x]) for x in table.keys()])
for i in range(0, max_i):
    for key in table.keys():
        try:
            if table[key][i] not in rows:
                rows[table[key][i]] = dict.fromkeys(table.keys(), "")
            rows[table[key][i]][key] = table[key][i]
        except:
            pass

print(",".join(table.keys()))
for i in sorted(rows):
    print(",".join(rows[i].values()))
